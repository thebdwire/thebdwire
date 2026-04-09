import feedparser
from flask import Flask, render_template
from datetime import datetime
import time

app = Flask(__name__)

# ─────────────────────────────────────────
# 📡 RSS FEED SOURCES — Bangladesh + Global
# ─────────────────────────────────────────
FEEDS = {
    # 🇧🇩 Bangladesh Sources
    "The Daily Star":     "https://www.thedailystar.net/rss.xml",
    "Dhaka Tribune":      "https://www.dhakatribune.com/feed",
    "bdnews24":           "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true",
    "Prothom Alo":        "https://www.prothomalo.com/feed",
    "Daily Bangladesh":   "https://www.daily-bangladesh.com/rss.xml",
    "Jugantor":           "https://www.jugantor.com/feed/rss.xml",
    "Samakal":            "https://samakal.com/feed",
    "Ittefaq":            "https://www.ittefaq.com.bd/feed",
    "New Age BD":         "https://www.newagebd.net/rss.xml",
    "Financial Express":  "https://thefinancialexpress.com.bd/feed",

    # 🌍 International Sources
    "Al Jazeera":         "https://www.aljazeera.com/xml/rss/all.xml",
    "BBC News":           "https://feeds.bbci.co.uk/news/rss.xml",
    "Reuters":            "https://feeds.reuters.com/reuters/topNews",
    "AP News":            "https://rsshub.app/apnews/topics/apf-topnews",
    "DW News":            "https://rss.dw.com/rdf/rss-en-all",
}

# ─────────────────────────────────────────
# 🏷️ SOURCE CATEGORIES
# ─────────────────────────────────────────
CATEGORIES = {
    "Bangladesh": ["The Daily Star", "Dhaka Tribune", "bdnews24", "Prothom Alo",
                   "Daily Bangladesh", "Jugantor", "Samakal", "Ittefaq",
                   "New Age BD", "Financial Express"],
    "International": ["Al Jazeera", "BBC News", "Reuters", "AP News", "DW News"],
}

# ─────────────────────────────────────────
# 🗄️ Simple In-Memory Cache (10 min TTL)
# ─────────────────────────────────────────
_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 600  # seconds

def fetch_news():
    global _cache
    now = time.time()

    if _cache["data"] and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["data"]

    news = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                image = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    image = entry.media_thumbnail[0].get("url")
                elif hasattr(entry, "media_content") and entry.media_content:
                    image = entry.media_content[0].get("url")

                category = "International"
                for cat, sources in CATEGORIES.items():
                    if source in sources:
                        category = cat
                        break

                news.append({
                    "source":   source,
                    "title":    entry.get("title", "No Title"),
                    "link":     entry.get("link", "#"),
                    "summary":  entry.get("summary", "")[:120] + "..." if entry.get("summary") else "",
                    "time":     entry.get("published", ""),
                    "image":    image,
                    "category": category,
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")

    _cache["data"] = news
    _cache["timestamp"] = now
    return news

@app.route("/")
def index():
    news = fetch_news()
    sources = list(FEEDS.keys())
    categories = CATEGORIES
    total = len(news)
    return render_template("index.html",
                           news=news,
                           sources=sources,
                           categories=categories,
                           total=total)

if __name__ == "__main__":
    app.run(debug=True)
