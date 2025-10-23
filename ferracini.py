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

class FerraciniScraper(BaseScraper):
    BASE_URL = "https://www.ferracini.com.br"

    def parse_product(self, soup , url):

        # Pegar o nome
        h1 = soup.find("div", class_ = "vtex-flex-layout-0-x-flexColChild pb0")
        nome = h1.get_text(strip=True) if h1 else None

        # Pegando o preço atual (com promo ou o normal quando não tem promo, se preco_original = None esse aqui é o normal)
        preco_container = soup.find('span',class_='vtex-product-price-1-x-currencyContainer vtex-product-price-1-x-currencyContainer--selling-price-pdp')
        preco_atual = parse_price(preco_container.get_text(strip=True)) if preco_container else None

        # Pegar a lista de tamanhos disponíveis
        divs_internas = [
            span for span in soup.find_all("span", class_="lojaferracini-store-theme-3GH_LJ5ygbbj6fvz8KrLCx")
            if span.get("class") == ["lojaferracini-store-theme-3GH_LJ5ygbbj6fvz8KrLCx"]
        ]
        tamanhos = [float(div.get_text(strip=True)) for div in divs_internas]

        # Pegar a imagem principal
        slider = soup.find("div", class_ ="vtex-store-components-3-x-triggerContainer vtex-store-components-3-x-triggerContainer--product-images bg-transparent pa0 bw0 dib")
        imagem_principal = slider.find("img").get("src")

        # Pegar preço original
        preco_container = soup.find('span',class_='vtex-product-price-1-x-currencyContainer vtex-product-price-1-x-currencyContainer--list-price-pdp')
        preco_original = parse_price(preco_container.get_text(strip=True)) if preco_container else None


        # Pegar se tem em estoque
        em_estoque = True if tamanhos else False

        # Moeda
        currency = "BRL"

        # Marca
        brand = "Ferracini"

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
    teste = FerraciniScraper()
    lista_sites = [
        'https://www.ferracini.com.br/tenis-masculino-couro-branco-dream-ferracini-9063-683d/p',
        "https://www.ferracini.com.br/sneaker-dream-9061-683a/p",
        "https://www.ferracini.com.br/sapato-casual-fluence-5552-559h/p",
    ]
    dics = teste.scrape_many(lista_sites)