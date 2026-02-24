import os, requests, anthropic
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SCRAPER_KEY = os.environ["SCRAPER_KEY"]

def scrape():
    url = "http://api.scraperapi.com?api_key="+SCRAPER_KEY+"&url=https://www.vinatis.com/achat-vin-promotion&render=true"
    r = requests.get(url, timeout=60)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for i in soup.select("div.product-item,li.product-item,article.product,.product_item"):
        n = i.select_one(".product-name,.name,h2,h3")
        p = i.select_one(".price,.product-price,.prix")
        if n and p: items.append(n.get_text(strip=True)+" | "+p.get_text(strip=True))
    if items: return "\n".join(items)
    lines = [l for l in soup.get_text(separator="\n",strip=True).split("\n") if len(l)>10]
    return "\n".join(lines[:300])

def ask_claude(txt):
    cl = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    p = "Tu es expert en vins francais. Voici le contenu de la page promotions de Vinatis:\n\n"+txt+"\n\nSelectionne environ 200eur de blancs francais, Loire en priorite, 15-30eur/bt. Signale Ruinart si present. Justifie chaque choix. Donne le total."
    return cl.messages.create(model="claude-haiku-4-5-20251001",max_tokens=1500,messages=[{"role":"user","content":p}]).content[0].text

def tg(txt):
    for i,ch in enumerate([txt[j:j+4000] for j in range(0,len(txt),4000)]):
        pre = "Vinatis du mois\n\n" if i==0 else ""
        requests.post("https://api.telegram.org/bot"+TELEGRAM_TOKEN+"/sendMessage",json={"chat_id":TELEGRAM_CHAT_ID,"text":pre+ch},timeout=15)

try: tg(ask_claude(scrape()))
except Exception as e: tg("Erreur: "+str(e))
