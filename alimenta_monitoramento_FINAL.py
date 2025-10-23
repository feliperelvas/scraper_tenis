"""
Esse código deve rodar umas 3x por dia para alimentar a tabela "monitoramento" com os preços e dados dos tênis que estão sendo monitorados.
"""

from dotenv import load_dotenv
import os
from supabase import create_client
import undo
import eurico

load_dotenv()  # carrega as variáveis do arquivo .env

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase = create_client(url, key)

TARGET_SIZES = [46.0, 46.5, 47.0]


### FUNÇÕES

def retornaListaMarcasMonitoradas():

    consulta = supabase.table("marcas_monitoradas") \
        .select("brand") \
        .execute()

    marcas = [row["brand"] for row in consulta.data]

    return marcas

def retornaIdMarca(marca):

    consulta = supabase.table("marcas_monitoradas") \
        .select("id") \
        .ilike("brand", marca) \
        .single() \
        .execute()

    brand_id = consulta.data["id"]

    return brand_id

def retornaListaDeLinksMonitoradosPorMarca(marca):

    brand_id = retornaIdMarca(marca)

    consulta = supabase.table("produtos_monitorados") \
    .select("site_url") \
    .eq("ativo", True) \
    .eq("brand_id", brand_id) \
    .execute()

    urls = [row["site_url"] for row in consulta.data]

    return urls

# Transforma de 2025-09-22T16:33:14-0300 para 2025-09-22 16:33:14
def corrigeFormatoData(timestamp):
    data_correta = timestamp.replace('T', " ").replace("-0300", "")
    return data_correta

def insereProdutoNoBD(produto, tamanho):

    data_correta = corrigeFormatoData(produto["timestamp"])

    brand_id = retornaIdMarca(produto["brand"])

    response = (
        supabase.table("monitoramento_tenis")
        .insert({
            "site": produto["site"],
            "name": produto["name"],
            "url": produto["url"],
            "price": produto["price"],
            "currency": produto["currency"],
            "size": tamanho,
            "timestamp": data_correta,
            "original_price": produto["original_price"],
            "in_stock": produto["in_stock"],
            "image_url": produto["image_url"],
            "brand_id": brand_id
        })
        .execute()
    )

def alimentaBancoComProdutosDaMarca(marca, objeto):

    urls = retornaListaDeLinksMonitoradosPorMarca(marca)
    dics = objeto.scrape_many(urls)

    for produto in dics:
        for size in TARGET_SIZES:
            if size in produto["sizes_available"]:
                insereProdutoNoBD(produto, size)

### MAIN

lista_marcas_monitoradas = retornaListaMarcasMonitoradas()

for marca in lista_marcas_monitoradas:
    if marca == "Undo":
        Undo = undo.UndoScraper()
        alimentaBancoComProdutosDaMarca(marca, Undo)
    elif marca == "Eurico":
        Eurico = eurico.EuricoScraper()
        alimentaBancoComProdutosDaMarca(marca, Eurico)