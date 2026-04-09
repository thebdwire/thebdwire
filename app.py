import feedparser
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

FEEDS = {
    "The Daily Star": "https://www.thedailystar.net/rss.xml",
    "Dhaka Tribune": "https://www.dhakatribune.com/feed",
    "bdnews24": "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true",
    "Prothom Alo": "https://www.prothomalo.com/feed",
    "Daily Bangladesh": "https://www.daily-bangladesh.com/rss.xml",
    "Jugantor": "https://www.jugantor.com/feed/rss.xml",
    "Samakal": "https://samakal.com/feed",
    "Ittefaq": "https://www.ittefaq.com.bd/feed",
}

def fetch_news():
    news = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                news.append({
                    "source": source,
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "#"),
                    "time": entry.get("published", ""),
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")
    return news

@app.route("/")
def index():
    news = fetch_news()
    sources = list(FEEDS.keys())
    return render_template("index.html", news=news, sources=sources)

if __name__ == "__main__":
    app.run(debug=True)
