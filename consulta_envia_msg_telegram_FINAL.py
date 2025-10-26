"""
A ideia do código é consultar a tabela de monitoramento e enviar uma msg no telegram com a lista de tênis que se enquadrarem nas condições.

CONDIÇÕES:
1) Produto estava fora de estoque e voltou para estoque.
2) Produto está com desconto.
    2.1) Se tem price e original_price
    2.2) Se o price é menor que o último armazenado.

RESPOSTA FINAL:
1) Produtos que voltaram ao estoque:
Produto 1: Foto + Nome + Preço + Link
Produto 2: Foto + Nome + Preço + Link
...

2) Produtos com desconto:
Produto 1: Foto + Nome + Preço + % Desconto + Link
Produto 2: Foto + Nome + Preço + % Desconto + Link
"""

from utils import enviaImagemTelegram
from datetime import timedelta
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
from utils import get_timestamp_gmt3_datetime

# -------------------------------------------------
# CONFIGURAÇÃO
# -------------------------------------------------
load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase = create_client(url, key)

TABLE = "monitoramento_tenis"       # ajuste se o nome for diferente
SIZES = [46, 47]         # tamanhos que você quer monitorar

# -------------------------------------------------
# DEFINE INTERVALO: ontem e hoje (00:00 -> agora)
# -------------------------------------------------

now = get_timestamp_gmt3_datetime()
start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

# -------------------------------------------------
# CONSULTA NO SUPABASE
# -------------------------------------------------
query = (
    supabase.table(TABLE)
    .select("url,timestamp,name,price,size,original_price,in_stock,image_url")
    .in_("size", SIZES)
    .gte("timestamp", start.isoformat())
    .lt("timestamp", end.isoformat())
    .order("url", desc=False)
    .order("size", desc=False)
    .order("timestamp", desc=True)
)

response = query.execute()
data = response.data or []

# -------------------------------------------------
# TRATA EM PANDAS (opcional)
# -------------------------------------------------
if data:
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

# -------------------------------------------------
# FUNÇÃO QUE VERIFICA SE VOLTOU PARA ESTOQUE
# -------------------------------------------------

def encontraProdutoQueVoltouParaEstoque(df):
    """
    Retorna um DF com os produtos (name + size) que em algum momento ficaram fora de estoque (False),
    depois viraram True E o último status é True (ou seja, voltaram e permanecem em estoque).

    Regras:
    - Ordena por timestamp dentro de cada (name, size)
    - Ignora casos que nunca ficaram False (sempre True)
    - Considera o ÚLTIMO False: se após ele existir algum True e o último registro for True, entra no resultado
    - Retorna o ÚLTIMO registro (estado atual) de cada (name, size) aprovado
    """
    df = df.copy()

    # Normaliza timestamp (com ou sem timezone)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    # Garante ordenação temporal por produto+tamanho
    df = df.sort_values(["name", "size", "timestamp"])

    aprovados = []
    for (_, _), grupo in df.groupby(["name", "size"], sort=False):
        grupo = grupo.sort_values("timestamp")

        # Posições onde ficou fora de estoque
        falses_idx = grupo.index[grupo["in_stock"] == False].tolist()
        if not falses_idx:
            # Nunca ficou fora -> não entra
            continue

        # Último 'False'
        last_false_idx = falses_idx[-1]

        # Verifica se após o último False houve algum True
        posterior = grupo.loc[grupo.index >= last_false_idx]
        voltou_true_depois = posterior["in_stock"].eq(True).any()

        # Último status atual
        ultimo_e_true = bool(grupo.iloc[-1]["in_stock"] == True)

        if voltou_true_depois and ultimo_e_true:
            # Guarda o último snapshot (o atual) desse name+size
            aprovados.append(grupo.iloc[-1])

    if not aprovados:
        # Retorna DF vazio com as mesmas colunas
        return pd.DataFrame(columns=df.columns)

    out = pd.DataFrame(aprovados).reset_index(drop=True)
    # Ordena por mais recente primeiro (opcional, só apresentação)
    out = out.sort_values("timestamp", ascending=False).reset_index(drop=True)
    return out


# -------------------------------------------------
# FUNÇÃO QUE VERIFICA SE O PRODUTO ESTÁ COM DESCONTO
# -------------------------------------------------

def encontraProdutoComDesconto(df):
    """
    Retorna um DF com os (name, size) que estão com desconto agora:

    Regra 1: se o ÚLTIMO registro tiver price e original_price preenchidos -> está com desconto.
    Regra 2: se NÃO houver original_price no último, comparar penúltimo vs último:
             incluir se price_ultimo < price_penultimo.

    Retorna somente o ÚLTIMO registro aprovado de cada (name, size).
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "original_price" in df.columns:
        df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")
    else:
        df["original_price"] = pd.NA

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    df = df.sort_values(["name", "size", "timestamp"])

    descontos = []
    for (_, _), grupo in df.groupby(["name", "size"], sort=False):
        grupo = grupo.sort_values("timestamp")
        if len(grupo) == 0:
            continue

        last = grupo.iloc[-1]

        # Regra 1: original_price preenchido no último registro + price preenchido
        if pd.notna(last.get("price")) and pd.notna(last.get("original_price")):
            descontos.append(last)
            continue

        # Regra 2: comparar últimos dois registros quando não há original_price no último
        if len(grupo) >= 2:
            penultimo = grupo.iloc[-2]
            if pd.notna(last.get("price")) and pd.notna(penultimo.get("price")):
                if float(last["price"]) < float(penultimo["price"]):
                    descontos.append(last)

    if not descontos:
        return pd.DataFrame(columns=df.columns)

    out = pd.DataFrame(descontos).reset_index(drop=True)
    out = out.sort_values("timestamp", ascending=False).reset_index(drop=True)
    return out


# -------------------------------------------------
# MAIN
# -------------------------------------------------

# Loop para o DF ESTOQUE
df_estoque = encontraProdutoQueVoltouParaEstoque(df)
for i, linha in df_estoque.iterrows():
    url = linha['url']
    timestamp = linha['timestamp']
    name = linha['name']
    price = linha['price']
    size = linha['size']
    original_price = linha['original_price']
    in_stock = linha['in_stock']
    image_url = linha['image_url']
    
    # Criar mensagem formatada em html
    mensagem = (
        f"<strong>Produto de volta ao estoque!</strong> ✅\n\n"
        f"- <strong>Nome:</strong> {name}\n"
        f"- <strong>Preço:</strong> R$ {price:.2f}\n"
    )

    if original_price and not pd.isna(original_price):
        mensagem += f"- <strong>Preço original:</strong> <strike>R$ {original_price:.2f}</strike>\n"

    mensagem += (
        f"- <strong>Tamanho:</strong> {size}\n"
        f"- <strong>Link do produto:</strong> {url}"
    )

    enviaImagemTelegram(url_imagem=image_url,legenda=mensagem)

# Loop para o DF PROMO
df_promo = encontraProdutoComDesconto(df)
for i, linha in df_promo.iterrows():
    url = linha['url']
    timestamp = linha['timestamp']
    name = linha['name']
    price = linha['price']
    size = linha['size']
    original_price = linha['original_price']
    in_stock = linha['in_stock']
    image_url = linha['image_url']

    # Calcular desconto (só se o preço original existir e for um número válido)
    linha_de_desconto = ""
    if original_price and not pd.isna(original_price):
        discount = (original_price - price) / original_price * 100
        linha_de_desconto = f"- <strong>Desconto:</strong> {discount:.0f}%\n"
    
    # Criar mensagem formatada em html
    mensagem = (
        f"<strong>Produto com desconto!</strong> ✅\n\n"
        f"- <strong>Nome:</strong> {name}\n"
        f"- <strong>Preço:</strong> R$ {price:.2f}\n"
    )

    if original_price and not pd.isna(original_price):
        mensagem += f"- <strong>Preço original:</strong> <strike>R$ {original_price:.2f}</strike>\n"

    mensagem += (
        linha_de_desconto +
        f"- <strong>Tamanho:</strong> {size}\n"
        f"- <strong>Link do produto:</strong> {url}"
    )

    enviaImagemTelegram(url_imagem=image_url,legenda=mensagem)