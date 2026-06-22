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
            "text": message
        },
        timeout=30
    )


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1280, "height": 900}
    )

    print("Apro Viagogo...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(8000)


    # Cookie / popup
    for selector in [
        "button:has-text('Accetta')",
        "button:has-text('Accetto')",
        "button:has-text('OK')",
        "button:has-text('Accept')",
        "[aria-label='Close']"
    ]:
        try:
            page.locator(selector).click(timeout=3000)
            print("Chiuso popup:", selector)
            break
        except:
            pass


    # Se chiede quantità, prova a scegliere 1
    for selector in [
        "text=1 biglietto",
        "text=1 biglietti",
        "text=1 Ticket",
        "text=1 ticket"
    ]:
        try:
            page.locator(selector).click(timeout=5000)
            print("Scelta quantità:", selector)
            break
        except:
            pass


    page.wait_for_timeout(10000)


    # salva screenshot per debug
    page.screenshot(
        path="viagogo-debug.png",
        full_page=True
    )


    text = page.locator("body").inner_text()

    browser.close()


print("Cerco prezzi...")

prices = []

patterns = [
    r"€\s*([0-9]+(?:[.,][0-9]{2})?)",
    r"([0-9]+(?:[.,][0-9]{2})?)\s*€"
]


for pattern in patterns:
    matches = re.findall(pattern, text)

    for m in matches:
        try:
            value = float(
                m.replace(".", "")
                 .replace(",", ".")
            )

            if 50 < value < 10000:
                prices.append(value)

        except:
            pass


if not prices:
    raise Exception(
        "Nessun prezzo trovato. Guarda lo screenshot viagogo-debug."
    )


lowest = min(prices)

print(f"Prezzo minimo trovato: {lowest} €")


if lowest <= THRESHOLD:

    send_telegram(
        f"🔥 Tomorrowland Weekend 1\n\n"
        f"🎟 1 biglietto trovato\n"
        f"💰 Prezzo minimo: {lowest:.2f} €\n"
        f"🎯 Soglia: {THRESHOLD} €\n\n"
        f"{URL}"
    )

else:
    print(
        f"Nessun alert. Minimo {lowest} € > {THRESHOLD} €"
    )
