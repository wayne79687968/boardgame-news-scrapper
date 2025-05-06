import pytest
from app import crawl_tgn

def test_crawl_tgn():
    articles = crawl_tgn()
    print("crawl_tgn 回傳：", articles)
    assert isinstance(articles, list), "回傳值應為 list"
    assert len(articles) > 0, "應該至少有一則新聞"
    for article in articles:
        assert isinstance(article, dict), "每則新聞應為 dict"
        assert 'title' in article, "每則新聞應包含 title 欄位"
        assert 'link' in article, "每則新聞應包含 link 欄位"
        assert article['title'], "title 不應為空"
        assert article['link'].startswith("https://www.tabletopgamingnews.com"), "link 應為 TGN 網址"