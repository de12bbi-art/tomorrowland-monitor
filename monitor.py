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

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page(
        viewport={
            "width": 1280,
            "height": 900
        }
    )

    print("Apro Viagogo...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(8000)


    # Cookie popup
    for selector in [
        "button:has-text('Accetta')",
        "button:has-text('Accetto')",
        "button:has-text('Accept')",
        "button:has-text('OK')",
        "[aria-label='Close']"
    ]:
        try:
            page.locator(selector).first.click(timeout=3000)
            print("Chiuso popup:", selector)
            break
        except:
            pass


    page.wait_for_timeout(3000)


    # Popup quantità biglietti
    print("Cerco quantità...")

    clicked = False

    for selector in [
        "button:has-text('1')",
        "[role='button']:has-text('1')",
        "text=1"
    ]:
        try:
            page.locator(selector).first.click(timeout=5000)
            print("Selezionato 1 biglietto:", selector)
            clicked = True
            break
        except:
            pass


    if not clicked:
        print("Click quantità non trovato")


    # Attendo caricamento listing
    page.wait_for_timeout(15000)


    # Screenshot
    page.screenshot(
        path="viagogo-debug.png",
        full_page=True
    )


    # Testo pagina
    text = page.locator("body").inner_text()

    print("===== TESTO PAGINA =====")
    print(text[:5000])


    # Salvo HTML completo
    html = page.content()

    with open(
        "viagogo-page.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)


    browser.close()



print("Cerco prezzi...")

prices = []


patterns = [
    r"€\s*([0-9]+(?:[.,][0-9]{2})?)",
    r"([0-9]+(?:[.,][0-9]{2})?)\s*€",
    r"EUR\s*([0-9]+(?:[.,][0-9]{2})?)"
]


for pattern in patterns:

    for m in re.findall(pattern, text):

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
        "Nessun prezzo trovato. Scarica viagogo-page.html"
    )



lowest = min(prices)

print(
    f"Prezzo minimo trovato: {lowest} €"
)



if lowest <= THRESHOLD:

    send_telegram(
        f"🔥 Tomorrowland Weekend 1\n\n"
        f"🎟 1 biglietto\n"
        f"💰 Prezzo minimo: {lowest:.2f} €\n"
        f"🎯 Soglia: {THRESHOLD} €\n\n"
        f"{URL}"
    )

else:

    print(
        f"Nessun alert: {lowest} € > {THRESHOLD} €"
    )
