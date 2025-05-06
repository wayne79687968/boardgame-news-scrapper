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
                time_tag = detail_soup.find('time')
                published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
                article.update({
                    "content": content,
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
        time_tag = detail_soup.find('time')
        published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
        first.update({
            "content": content,
            "published": published
        })
        articles[0] = first
    return articles

def crawl_tgn():
    url = "https://www.tabletopgamingnews.com/feed"
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
            content_tag = detail_soup.select_one('div.entry-content.single-content')
            content = content_tag.get_text(separator='\n', strip=True) if content_tag else None
            time_tag = detail_soup.find('time')
            published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
            article.update({
                "content": content,
                "published": published
            })
        articles.append(article)
    # 無論是否為今日新聞，第一則都要補抓內容
    if articles and not found_today:
        first = articles[0]
        detail_res = requests.get(first['link'], headers=HEADERS)
        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
        content_tag = detail_soup.select_one('div.entry-content.single-content')
        content = content_tag.get_text(separator='\n', strip=True) if content_tag else None
        time_tag = detail_soup.find('time')
        published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
        first.update({
            "content": content,
            "published": published
        })
        articles[0] = first
    return articles

def crawl_boardgamewire():
    url = "https://boardgamewire.com/"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = []
    for card in soup.select('article.entry-card')[:5]:
        title_tag = card.select_one('h2.entry-title a')
        link = title_tag['href'] if title_tag else None
        title = title_tag.get_text(strip=True) if title_tag else None
        image_tag = card.select_one('img')
        image = image_tag['data-src'] if image_tag and image_tag.has_attr('data-src') else (image_tag['src'] if image_tag and image_tag.has_attr('src') else None)
        author_tag = card.select_one('li.meta-author span[itemprop="name"]')
        author = author_tag.get_text(strip=True) if author_tag else None
        time_tag = card.select_one('li.meta-date time')
        published = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
        articles.append({
            "title": title,
            "link": link,
            "image": image,
            "author": author,
            "published": published
        })
    # 抓第一則詳細內容
    if articles and articles[0]['link']:
        detail_url = articles[0]['link']
        detail_res = requests.get(detail_url, headers=HEADERS)
        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
        # 先嘗試 article .entry-content
        content_tag = detail_soup.select_one('article .entry-content')
        if not content_tag:
            content_tag = detail_soup.find('div', class_='entry-content')
        content = content_tag.get_text(separator='\n', strip=True) if content_tag else None
        articles[0]['content'] = content
    return articles

@app.route("/news")
def get_news():
    return jsonify({
        "dicebreaker": crawl_dicebreaker(),
        "meeples_herald": crawl_meeples_herald(),
        "tgn": crawl_tgn(),
        "boardgamewire": crawl_boardgamewire()
    })

@app.route("/")
def index():
    return "桌遊新聞爬蟲 API 已啟動！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)