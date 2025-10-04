import requests
from bs4 import BeautifulSoup
import time
from utils import get_timestamp_gmt3

"""
Exemplo do json:

- site (string): dominio de qual loja veio.
- name (string): nome do produto.
- url (string): link direto pro produto.
- price (float): preço atual.
- currency (string, default "BRL"): para padronizar, mesmo que por enquanto seja só reais.
- sizes_available (lista de float/int): lista de números (ex.: [34, 35, 36]).
- timestamp (ISO 8601 string): quando o dado foi coletado (pra comparar histórico).
- original_price (float): se tiver preço cheio e preço promocional, isso é útil pra calcular desconto.
- in_stock (bool): true se tiver ao menos um tamanho disponível.
- image_url (string): URL da imagem principal.
- brand (string): ex.: "Nike".
"""

class BaseScraper:
    BASE_URL = ""

    def __init__(self, timeout = 15, user_agent = None):
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.user_agent
            }
        )
        
    def fetch(self, url):
        resposta = self.session.get(url, timeout=self.timeout)
        resposta.raise_for_status()
        return BeautifulSoup(resposta.text, "html.parser")
    
    def scrape_product(self, url):
        soup = self.fetch(url)
        data = self.parse_product(soup, url)
        data.setdefault("url", url)
        data.setdefault("site", self.BASE_URL)
        data.setdefault("currency", "BRL")
        data.setdefault("timestamp",get_timestamp_gmt3())
        return data
    
    def scrape_many(self, url_list = [], sleep = 0.3):
        saidas = []
        for url in url_list:
            try:
                saidas.append(self.scrape_product(url))
            except requests.HTTPError as e:
                saidas.append({"url": url, "error": f"HTTP {e.response.status_code}"})
            except Exception as e:
                saidas.append({"url": url, "error": str(e)})
            if sleep:
                time.sleep(sleep)
        return saidas

    def parse_product(self, soup, url):
        raise NotImplementedError
    
