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
