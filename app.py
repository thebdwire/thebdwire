import feedparser
import time
from flask import Flask, render_template

app = Flask(__name__)

# ── Bangladesh-Only Sources ──────────────────────────────────────────────────
FEEDS = {
    "Prothom Alo":       "https://www.prothomalo.com/feed",
    "Daily Star":        "https://www.thedailystar.net/rss.xml",
    "Dhaka Tribune":     "https://www.dhakatribune.com/feed",
    "bdnews24":          "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true",
    "New Age BD":        "https://www.newagebd.net/rss.xml",
    "Financial Express": "https://thefinancialexpress.com.bd/feed",
    "Daily Bangladesh":  "https://www.daily-bangladesh.com/rss.xml",
    "Ittefaq":           "https://www.ittefaq.com.bd/feed",
    "Jugantor":          "https://www.jugantor.com/feed/rss.xml",
    "Samakal":           "https://samakal.com/feed",
}

# ── Categories ───────────────────────────────────────────────────────────────
CATEGORIES = {
    "National":         ["dhaka","chittagong","sylhet","khulna","rajshahi","barisal",
                         "mymensingh","district","local","village","union","upazila",
                         "thana","police","administration"],
    "Politics":         ["election","government","minister","parliament","party","political",
                         "vote","prime minister","president","cabinet","ruling","opposition",
                         "awami","bnp","jamat","hasina","khaleda"],
    "World":            ["india","china","usa","uk","saudi","qatar","malaysia","myanmar",
                         "rohingya","diplomat","foreign","embassy","consulate","visa","passport"],
    "Economy":          ["economy","gdp","inflation","budget","bank","taka","market","finance",
                         "investment","revenue","remittance","loan"],
    "Trade & Commerce": ["company","business","stock","shares","profit","industry","startup",
                         "factory","tender","contract","deal","export","import","port",
                         "customs","trade"],
    "Sports":           ["cricket","football","sport","match","tournament","team","player",
                         "game","cup","bpl","dhaka premier","bangladesh premier","kabaddi"],
}

# ── Strict Bangladesh filter (50+ keywords) ──────────────────────────────────
BD_KEYWORDS = [
    "bangladesh","dhaka","chittagong","sylhet","khulna","rajshahi","barisal","mymensingh",
    "comilla","narayanganj","gazipur","narsingdi","tangail","netrokona","jamalpur","sherpur",
    "gopalgonj","faridpur","madaripur","rajbari","taka","crore","lakh","muktijoddha",
    "bnp","awami league","jamat","khaleda","hasina","sheikh hasina","khaleda zia",
    "padma","meghna","jamuna","sundarbans","cox's bazar","rohingya","rmg","epz",
    "bepza","bgmea","bdnews","prothom alo","daily star","dhaka tribune",
]

def classify_category(title, summary):
    text = (title + " " + summary).lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return cat
    return "National"

def is_bangladesh_relevant(title, summary):
    text = (title + " " + summary).lower()
    return any(kw in text for kw in BD_KEYWORDS)

_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 600  # 10 minutes

def fetch_news():
    global _cache
    now = time.time()
    if _cache["data"] and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["data"]

    news = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                title   = entry.get("title", "No Title")
                summary = entry.get("summary", "")
                if not is_bangladesh_relevant(title, summary):
                    continue
                image = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    image = entry.media_thumbnail[0].get("url")
                elif hasattr(entry, "media_content") and entry.media_content:
                    image = entry.media_content[0].get("url")
                category      = classify_category(title, summary)
                clean_summary = summary[:160] + "..." if len(summary) > 160 else summary
                news.append({
                    "source":   source,
                    "title":    title,
                    "link":     entry.get("link", "#"),
                    "summary":  clean_summary,
                    "time":     entry.get("published", ""),
                    "image":    image,
                    "category": category,
                })
        except Exception:
            pass

    _cache["data"]      = news
    _cache["timestamp"] = now
    return news

@app.route("/")
def index():
    news       = fetch_news()
    categories = ["All"] + sorted(set(n["category"] for n in news))
    total      = len(news)
    return render_template("index.html", news=news, categories=categories, total=total)

if __name__ == "__main__":
    app.run(debug=True)
