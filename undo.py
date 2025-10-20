from base import BaseScraper
from utils import parse_price, get_timestamp_gmt3

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

class UndoScraper(BaseScraper):
    BASE_URL = "https://undostore.com"

    def parse_product(self, soup , url):

        # Pegar o nome
        h1 = soup.find("h1")
        nome = h1.get_text(strip=True) if h1 else None

        # Pegar o preço atual
        spans = soup.find("div", class_="text-copy").find_all("span", recursive=False)
        preco_atual = parse_price(spans[1].get_text(strip=True)) # já pega o preço em promo

        # Pegar a lista de tamanhos disponíveis
        divs_internas = soup.find("div", class_ = "product-sariants group grid w-full grid-cols-4 justify-between gap-[1px] md:grid-cols-5").find_all("div", {"data-original-available": "true"} ,recursive=False)
        tamanhos = [float(div.get("data-value")[3:]) for div in divs_internas if div.get("data-value")]

        # Pegar a imagem principal
        slider = soup.find("div", id="product-slider")
        imagens = [a["href"] for a in slider.find_all("a", href=True)]
        imagem_principal = "https:" + imagens[0]

        # Pegar preço original
        span = soup.find("span", class_="strike w-fit opacity-50")
        preco_original = parse_price(span.get_text(strip=True)) if span else None

        # Pegar se tem em estoque
        em_estoque = True if tamanhos else False

        # Moeda
        currency = "BRL"

        # Marca
        brand = "Undo"

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
    teste = UndoScraper()
    lista_sites = [
        'https://undostore.com/products/rio-vanilla-rainbow',
        "https://undostore.com/products/nuven-2-1-high-black-bird",
        "https://undostore.com/products/jaguar-dune",
        "https://undostore.com/products/nuven-2-1-vanilla-rainbow"
    ]
    dics = teste.scrape_many(lista_sites)