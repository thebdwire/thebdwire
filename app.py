import feedparser
import time
from flask import Flask, render_template

app = Flask(__name__)

# ─────────────────────────────────────────
# 📡 Bangladesh-Only RSS Sources
# ─────────────────────────────────────────
FEEDS = {
    "The Daily Star":    "https://www.thedailystar.net/rss.xml",
    "Dhaka Tribune":     "https://www.dhakatribune.com/feed",
    "bdnews24":          "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true",
    "Prothom Alo":       "https://www.prothomalo.com/feed",
    "Daily Bangladesh":  "https://www.daily-bangladesh.com/rss.xml",
    "Jugantor":          "https://www.jugantor.com/feed/rss.xml",
    "Samakal":           "https://samakal.com/feed",
    "Ittefaq":           "https://www.ittefaq.com.bd/feed",
    "New Age BD":        "https://www.newagebd.net/rss.xml",
    "Financial Express": "https://thefinancialexpress.com.bd/feed",
}

# ─────────────────────────────────────────
# 🏷️ Topic Classification by Keywords
# ─────────────────────────────────────────
TOPICS = {
    "Politics":  ["election","government","minister","parliament","party","political",
                  "vote","prime minister","president","cabinet","ruling","opposition","coup","rally"],
    "Economy":   ["economy","gdp","inflation","budget","trade","bank","taka","market",
                  "finance","investment","revenue","remittance","export","import","loan","fiscal"],
    "Sports":    ["cricket","football","sport","match","tournament","team","player",
                  "game","cup","goal","ipl","bpl","olympic","athlete","coach","series"],
    "Crime":     ["arrest","murder","crime","police","court","verdict","accused","case",
                  "robbery","drug","killed","rape","assault","detained","sentenced","corruption"],
    "Business":  ["company","business","stock","shares","profit","industry","entrepreneur",
                  "startup","factory","ceo","launch","merger","acquisition","tender","contract"],
    "Health":    ["health","hospital","disease","medicine","doctor","covid","dengue","virus",
                  "patient","treatment","vaccine","outbreak","surgery","clinic","mental health"],
    "Education": ["education","university","school","student","exam","result","scholarship",
                  "teacher","admission","tuition","curriculum","campus","degree","research"],
    "Tech":      ["technology","digital","internet","app","software","ai","startup","cyber",
                  "mobile","innovation","data","robot","computer","blockchain","satellite"],
}

def classify_topic(title, summary):
    text = (title + " " + summary).lower()
    for topic, keywords in TOPICS.items():
        for kw in keywords:
            if kw in text:
                return topic
    return "General"

# ─────────────────────────────────────────
# 🗄️ In-Memory Cache (10 min TTL)
# ─────────────────────────────────────────
_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 600

def fetch_news():
    global _cache
    now = time.time()
    if _cache["data"] and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["data"]

    news = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                image = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    image = entry.media_thumbnail[0].get("url")
                elif hasattr(entry, "media_content") and entry.media_content:
                    image = entry.media_content[0].get("url")

                title   = entry.get("title", "No Title")
                summary = entry.get("summary", "")
                topic   = classify_topic(title, summary)

                news.append({
                    "source":  source,
                    "title":   title,
                    "link":    entry.get("link", "#"),
                    "summary": summary[:130] + "..." if len(summary) > 130 else summary,
                    "time":    entry.get("published", ""),
                    "image":   image,
                    "topic":   topic,
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")

    _cache["data"] = news
    _cache["timestamp"] = now
    return news

@app.route("/")
def index():
    news   = fetch_news()
    topics = ["All"] + sorted(set(n["topic"] for n in news))
    total  = len(news)
    return render_template("index.html", news=news, topics=topics, total=total)

if __name__ == "__main__":
    app.run(debug=True)
