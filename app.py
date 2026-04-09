import feedparser
import datetime
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = Flask(__name__)

FEEDS = {
    "The Daily Star": "https://www.thedailystar.net/feed",
    "bdnews24": "https://bdnews24.com/feed",
    "Dhaka Tribune": "https://www.dhakatribune.com/feed",
    "Prothom Alo (English)": "https://en.prothomalo.com/feed",
    "Reuters (Bangladesh)": "https://feeds.reuters.com/reuters/bangladeshNews",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "BBC South Asia": "http://feeds.bbci.co.uk/news/world/south_asia/rss.xml",
    "AP News": "https://rsshub.app/apnews/topics/bangladesh",
}

articles = []
last_updated = "Never"

def fetch_feeds():
    global articles, last_updated
    fresh = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                fresh.append({
                    "source": source,
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "#"),
                    "summary": entry.get("summary", "")[:200],
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"[The BD Wire] Error fetching {source}: {e}")
    articles = fresh
    last_updated = datetime.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    print(f"[The BD Wire] Feed refreshed at {last_updated} — {len(articles)} articles loaded.")

fetch_feeds()

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_feeds, "interval", minutes=30)
scheduler.start()

@app.route("/")
def index():
    return render_template("index.html", articles=articles, last_updated=last_updated)

@app.route("/refresh")
def refresh():
    fetch_feeds()
    return f"Refreshed! {len(articles)} articles loaded at {last_updated}"

if __name__ == "__main__":
    app.run(debug=True)
