from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0"}

def crawl_dicebreaker():
    url = "https://www.dicebreaker.com/archive/news"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.select("a.card--horizontal")[:5]
    return [{
        "title": a.select_one("h3.card__title").text.strip(),
        "url": "https://www.dicebreaker.com" + a['href']
    } for a in articles if a.select_one("h3.card__title")]

def crawl_meeples_herald():
    url = "https://meeplesherald.com/"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.select(".jeg_post_title a")[:5]
    return [{"title": a.text.strip(), "url": a['href']} for a in articles]

@app.route("/news")
def get_news():
    return jsonify({
        "dicebreaker": crawl_dicebreaker(),
        "meeples_herald": crawl_meeples_herald()
    })

@app.route("/")
def index():
    return "桌遊新聞爬蟲 API 已啟動！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)