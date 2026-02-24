import os, requests, anthropic
from bs4 import BeautifulSoup
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
URL = "https://www.vinatis.com/achat-vin-promotion"
H = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36"}
def scrape():
    r = requests.get(URL, headers=H, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for i in soup.select("div.product-item,li.product-item,article.product"):
        n = i.select_one(".product-name,h2,h3")
        p = i.select_one(".price,.product-price")
        if n and p: items.append(n.get_text(strip=True)+" | "+p.get_text(strip=True))
    return "\n".join(items) if items else soup.get_text()[:12000]
def ask_claude(txt):
    cl = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    p = "Expert vins francais: selectionne 200eur blancs francais Loire 15-30eur/bt. Ruinart si promo. Justifie chaque choix. Total. Promos: " + txt
    return cl.messages.create(model="claude-haiku-4-5-20251001",max_tokens=1500,messages=[{"role":"user","content":p}]).content[0].text
def tg(txt):
    for i,ch in enumerate([txt[j:j+4000] for j in range(0,len(txt),4000)]):
        pre = "Vinatis du mois\n\n" if i==0 else ""
        requests.post("https://api.telegram.org/bot"+TELEGRAM_TOKEN+"/sendMessage",json={"chat_id":TELEGRAM_CHAT_ID,"text":pre+ch},timeout=15)
try: tg(ask_claude(scrape()))
except Exception as e: tg("Erreur: "+str(e))
