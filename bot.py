import os, requests, anthropic
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
VINATIS_URL = "https://www.vinatis.com/achat-vin-promotion"

def scrape():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    try:
        r = requests.get(VINATIS_URL, headers=headers, timeout=30)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        for i in soup.select("div.product-item,li.product-item,article.product,.product_item,.item-product"):
            n = i.select_one(".product-name,.name,h2,h3")
            p = i.select_one(".price,.product-price,.prix")
            if n and p: items.append(n.get_text(strip=True)+" | "+p.get_text(strip=True))
        if items: return "\n".join(items)
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.split("\n") if l and len(l)>10]
        return "\n".join(lines[:300])
    except Exception as e:
        return "Impossible de scraper Vinatis: "+str(e)

def ask_claude(txt):
    cl = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    p = "Tu es expert en vins francais. Voici le contenu de la page promotions de Vinatis:\n\n"+txt+"\n\nSi tu trouves des vins en promo: selectionne environ 200eur de blancs francais, Loire en priorite, 15-30eur/bt, justifie chaque choix, signale Ruinart si present, donne le total. Si le contenu ne contient pas de vins, dis-le clairement et explique."
    return cl.messages.create(model="claude-haiku-4-5-20251001",max_tokens=1500,messages=[{"role":"user","content":p}]).content[0].text

def tg(txt):
    for i,ch in enumerate([txt[j:j+4000] for j in range(0,len(txt),4000)]):
        pre = "Vinatis du mois\n\n" if i==0 else ""
        requests.post("https://api.telegram.org/bot"+TELEGRAM_TOKEN+"/sendMessage",json={"chat_id":TELEGRAM_CHAT_ID,"text":pre+ch},timeout=15)

try: tg(ask_claude(scrape()))
except Exception as e: tg("Erreur: "+str(e))
