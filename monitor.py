import os
import re
import requests
from playwright.sync_api import sync_playwright

URL = "https://www.viagogo.it/Biglietti-Festivals/Festival-Internazionali/Tomorrowland-Biglietti/E-160250859?quantity=1"

THRESHOLD = 500

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=30,
    )


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, wait_until="networkidle", timeout=120000)

    text = page.locator("body").inner_text()

    browser.close()

prices = []

patterns = [
    r"€\s*([0-9]+(?:[.,][0-9]{2})?)",
    r"([0-9]+(?:[.,][0-9]{2})?)\s*€",
]

for pattern in patterns:
    for m in re.findall(pattern, text):
        try:
            value = float(m.replace(".", "").replace(",", "."))
            if 50 < value < 10000:
                prices.append(value)
        except:
            pass

if not prices:
    raise Exception("Nessun prezzo trovato nemmeno con Playwright")

lowest = min(prices)

print("Lowest:", lowest)

if lowest <= THRESHOLD:
    send_telegram(
        f"🔥 Tomorrowland Weekend 1\n\n"
        f"Prezzo minimo: €{lowest:.2f}\n"
        f"Soglia: €{THRESHOLD}"
    )
