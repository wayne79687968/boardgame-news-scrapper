from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

app = Flask(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0"}

def crawl_dicebreaker():
    url = "https://www.dicebreaker.com/feed/news"
    res = requests.get(url, headers=HEADERS)
    ns = {
        'media': 'http://search.yahoo.com/mrss/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    root = ET.fromstring(res.content)
    channel = root.find('channel')
    items = channel.findall('item')[:5]
    articles = []
    today = datetime.utcnow().date()
    found_today = False
    for idx, item in enumerate(items):
        categories = [c.text for c in item.findall('category')]
        image = None
        media_content = item.find('media:content', ns)
        if media_content is not None:
            image = media_content.attrib.get('url')
        pub_date_str = item.findtext('pubDate')
        pub_date = None
        if pub_date_str:
            try:
                pub_date = datetime.strptime(pub_date_str[:16], "%a, %d %b %Y").date()
            except Exception:
                pass
        article = {
            "title": item.findtext('title'),
            "link": item.findtext('link'),
            "creator": item.findtext('dc:creator', namespaces=ns),
            "pubDate": pub_date_str,
            "guid": item.findtext('guid'),
            "categories": categories,
            "image": image,
            "description": item.findtext('description')
        }
        # 若日期為今天，進一步爬取內容
        if pub_date == today:
            found_today = True
            detail_res = requests.get(article['link'], headers=HEADERS)
            detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
            content_tag = detail_soup.find('div', class_='article_body_content')
            content = content_tag.get_text(separator='\n', strip=True) if content_tag else None
            author_tag = detail_soup.select_one('a.author-card__link')
            author = author_tag.get_text(strip=True) if author_tag else None
            time_tag = detail_soup.find('time')
            published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
            article.update({
                "content": content,
                "author": author,
                "published": published
            })
        articles.append(article)
    # 無論是否為今日新聞，第一則都要補抓內容
    if articles and not found_today:
        first = articles[0]
        detail_res = requests.get(first['link'], headers=HEADERS)
        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
        content_tag = detail_soup.find('div', class_='article_body_content')
        content = content_tag.get_text(separator='\n', strip=True) if content_tag else None
        author_tag = detail_soup.select_one('a.author-card__link')
        author = author_tag.get_text(strip=True) if author_tag else None
        time_tag = detail_soup.find('time')
        published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
        first.update({
            "content": content,
            "author": author,
            "published": published
        })
        articles[0] = first
    return articles

def crawl_meeples_herald():
    url = "https://meeplesherald.com/news/"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = []
    today = datetime.utcnow().date()
    found_today = False
    latest_article = None
    latest_article_link = None
    for idx, h3 in enumerate(soup.select('h3.entry-title')):
        a = h3.find('a')
        if a and a.text and a['href']:
            article = {
                "title": a.text.strip(),
                "link": a['href']
            }
            # 取得該篇文章的父元素，尋找日期
            parent = h3.parent
            date_str = None
            date_tag = parent.find(class_='jeg_meta_date') or parent.find(class_='jeg_post_date')
            if date_tag:
                date_str = date_tag.text.strip()
            if not date_str:
                date_tag = h3.find_next(class_='jeg_meta_date') or h3.find_next(class_='jeg_post_date')
                if date_tag:
                    date_str = date_tag.text.strip()
            pub_date = None
            if date_str:
                try:
                    pub_date = datetime.strptime(date_str, "%B %d, %Y").date()
                except Exception:
                    try:
                        pub_date = datetime.strptime(date_str, "%b %d, %Y").date()
                    except Exception:
                        pass
            # 記錄最新一則
            if latest_article is None:
                latest_article = article
                latest_article_link = a['href']
            # 若日期為今天，進一步爬取內容
            if pub_date == today:
                found_today = True
                detail_res = requests.get(a['href'], headers=HEADERS)
                detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                content_tag = detail_soup.find('div', class_='td-post-content')
                content = content_tag.get_text(separator='\\n', strip=True) if content_tag else None
                author_tag = detail_soup.select_one('div.td-post-author-name a')
                author = author_tag.get_text(strip=True) if author_tag else None
                time_tag = detail_soup.find('time')
                published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
                article.update({
                    "content": content,
                    "author": author,
                    "published": published
                })
            articles.append(article)
            if len(articles) >= 5:
                break
    # 無論是否為今日新聞，第一則都要補抓內容
    if articles and (not found_today or True):
        first = articles[0]
        detail_res = requests.get(first['link'], headers=HEADERS)
        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
        content_tag = detail_soup.find('div', class_='td-post-content')
        content = content_tag.get_text(separator='\\n', strip=True) if content_tag else None
        author_tag = detail_soup.select_one('div.td-post-author-name a')
        author = author_tag.get_text(strip=True) if author_tag else None
        time_tag = detail_soup.find('time')
        published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
        first.update({
            "content": content,
            "author": author,
            "published": published
        })
        articles[0] = first
    return articles

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