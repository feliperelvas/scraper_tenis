from base import BaseScraper
from utils import parse_price, get_timestamp_gmt3
import re, json

"""
Exemplo do json:

- site (string): de qual loja veio (bom pra quando você tiver vários scrapers).
- name (string): nome do produto.
- url (string): link direto pro produto.
- price (float): preço atual.
- currency (string, default "BRL"): para padronizar, mesmo que por enquanto seja só reais.
- size (float): número referente ao tamanho do tênis (ex.: 36).
- timestamp (ISO 8601 string): quando o dado foi coletado (pra comparar histórico).
- original_price (float): se tiver preço cheio e preço promocional, isso é útil pra calcular desconto.
- in_stock (bool): true se tiver ao menos um tamanho disponível.
- image_url (string): URL da imagem principal (útil se for mandar pro Telegram).
- brand_id (float): ex.: "1" referente a Undo.
"""

class AsicsScraper(BaseScraper):
    BASE_URL = "https://www.asics.com.br"

    def parse_product(self, soup , url):

        # Pegar o nome
        nome_tag = soup.select_one("section.prod-top--infos__name div.fn.productName")
        nome = nome_tag.get_text(strip=True) if nome_tag else None

        # Pegando o preço atual (com promo ou o normal quando não tem promo, se preco_original = None esse aqui é o normal)
        preco_container = soup.select_one("section.prod-top--infos__price strong.skuBestPrice")
        preco_atual = parse_price(preco_container.get_text(strip=True)) if preco_container else None

        # Pegar a lista de tamanhos disponíveis
        script = soup.find("script", string=re.compile(r"var\s+skuJson_0\s*="))
        tamanhos = []

        if script:
            m = re.search(r'var\s+skuJson_0\s*=\s*(\{.*?\});\s*CATALOG_SDK', script.string, re.S)
            if m:
                data = json.loads(m.group(1))
                for sku in data.get("skus", []):
                    if sku.get("available"):  # só os disponíveis
                        t = sku.get("dimensions", {}).get("Tamanhos")
                        if t:
                            try:
                                tamanhos.append(float(t.replace(",", ".")))
                            except ValueError:
                                pass

        # Pegar a imagem principal
        mt = soup.find("meta", {"property": "og:image"})
        imagem_principal = mt.get("content", "").strip() if mt else None

        # Pegar preço original
        preco_container = soup.select_one("section.prod-top--infos__price strong.skuListPrice")
        preco_original = parse_price(preco_container.get_text(strip=True)) if preco_container else None
        if preco_original == 0.0: preco_original = None # Preciso fazer isso porque quando não está em promo, o valor original vem zerado. Então, para não parecer que é um grande desconto coloco None

        # Pegar se tem em estoque
        em_estoque = True if tamanhos else False

        # Moeda
        currency = "BRL"

        # Marca
        brand = "Asics"

        # timestamp
        timestamp = get_timestamp_gmt3()

        return {
            "site": self.BASE_URL,
            "name": nome,
            "url": url,
            "price": preco_atual,
            "currency": currency,
            "sizes_available": tamanhos,
            "timestamp": timestamp,
            "original_price": preco_original,
            "in_stock": em_estoque,
            "image_url": imagem_principal,
            "brand": brand
        }
    

if __name__ == "__main__":
    teste = AsicsScraper()
    lista_sites = [
        'https://www.asics.com.br/1011b974-405/p',
        "https://www.asics.com.br/1201a555-005/p",
        "https://www.asics.com.br/1011b963-001/p",
        "https://www.asics.com.br/1011b984-400/p"
    ]
    dics = teste.scrape_many(lista_sites)