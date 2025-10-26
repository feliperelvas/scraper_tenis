# scraper/utils.py

from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # carrega as variáveis do arquivo .env

TOKEN = os.environ["TOKEN_TELEGRAM"]
CHAT_ID = os.environ["CHATID_TELEGRAM"]

def parse_price(txt):
    if not txt:
        return None
    return float(txt.replace("R$", "").replace(".", "").replace(",", ".").strip())

# fuso horário GMT-3 (fixo)
GMT_MINUS_3 = timezone(timedelta(hours=-3))

def get_timestamp_gmt3() -> str:
    """
    Retorna timestamp no formato ISO 8601 no fuso GMT-3.
    Exemplo: "2025-09-06T17:14:30-0300"
    """
    return datetime.now(GMT_MINUS_3).strftime("%Y-%m-%dT%H:%M:%S%z")

def get_timestamp_gmt3_datetime() -> datetime:
    """
    Retorna timestamp no formato ISO 8601 no fuso GMT-3.
    Exemplo: "2025-09-06T17:14:30-0300"
    """
    return datetime.now(GMT_MINUS_3)

# Enviando uma mensagem
def enviaTextoTelegram(mensagem):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "html"}

    r = requests.get(url, params=params)

# Enviando uma imagem
def enviaImagemTelegram(url_imagem, legenda):

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    data = {"chat_id": CHAT_ID, "photo": url_imagem, "caption": legenda, "parse_mode": "html"}
    r = requests.post(url, data=data)