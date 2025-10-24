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

from utils import enviaImagemTelegram, enviaTextoTelegram

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
print(f"🔹 Registros retornados: {len(data)}")

# -------------------------------------------------
# TRATA EM PANDAS (opcional)
# -------------------------------------------------
if data:
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    print(df.head(10))
else:
    print("Nenhum dado encontrado para ontem e hoje.")

# -------------------------------------------------
# FUNÇÃO QUE VERIFICA SE VOLTOU PARA ESTOQUE -> preciso testar com casos reais
# -------------------------------------------------

def find_back_in_stock(df):
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
