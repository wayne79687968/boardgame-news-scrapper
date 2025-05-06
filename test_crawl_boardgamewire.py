import pytest
from app import crawl_boardgamewire

def test_crawl_boardgamewire():
    articles = crawl_boardgamewire()
    print("crawl_boardgamewire 回傳：", articles)
    assert isinstance(articles, list), "回傳值應為 list"
    assert len(articles) > 0, "應該至少有一則新聞"
    for article in articles:
        assert isinstance(article, dict), "每則新聞應為 dict"
        assert 'title' in article, "每則新聞應包含 title 欄位"
        assert 'link' in article, "每則新聞應包含 link 欄位"
        assert article['title'], "title 不應為空"
        assert article['link'].startswith("https://boardgamewire.com/"), "link 應為 boardgamewire 網址"
    # 第一則要有 content 欄位
    assert 'content' in articles[0], "第一則應包含 content 欄位"
    assert articles[0]['content'], "content 不應為空"