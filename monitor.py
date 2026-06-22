import os
import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.viagogo.it/Biglietti-Festivals/Festival-Internazionali/Tomorrowland-Biglietti/E-160250859?quantity=1"

THRESHOLD = 500

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )


headers = {
    "User-Agent": (
        "Mozilla/5.0"
    )
}

response = requests.get(URL, headers=headers, timeout=30)

if response.status_code != 200:
    raise Exception(f"HTTP {response.status_code}")

html = response.text

prices = []

# Cerca prezzi in euro nel codice sorgente
matches = re.findall(r"€\s*([0-9]+(?:[.,][0-9]{2})?)", html)

for m in matches:
    try:
        value = float(m.replace(".", "").replace(",", "."))
        prices.append(value)
    except:
        pass

if not prices:
    raise Exception("Nessun prezzo trovato")

lowest = min(prices)

print("Lowest:", lowest)

if lowest <= THRESHOLD:
    send_telegram(
        f"🔥 Tomorrowland Weekend 1\n\n"
        f"Prezzo minimo trovato: €{lowest:.2f}\n"
        f"Soglia: €{THRESHOLD}"
    )