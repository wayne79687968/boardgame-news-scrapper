import pytest
from app import crawl_dicebreaker
from app import crawl_meeples_herald


def test_crawl_dicebreaker():
    articles = crawl_dicebreaker()
    print("crawl_dicebreaker 回傳：", articles)
    assert isinstance(articles, list), "回傳值應為 list"
    assert len(articles) > 0, "應該至少有一則新聞"
    for article in articles:
        assert isinstance(article, dict), "每則新聞應為 dict"
        assert 'title' in article, "每則新聞應包含 title 欄位"
        assert 'link' in article, "每則新聞應包含 link 欄位"
        assert article['title'], "title 不應為空"
        assert article['link'].startswith("https://www.dicebreaker.com"), "link 應為 dicebreaker 網址"

def test_crawl_meeples_herald():
    articles = crawl_meeples_herald()
    print("crawl_meeples_herald 回傳：", articles)
    assert isinstance(articles, list), "回傳值應為 list"
    assert len(articles) > 0, "應該至少有一則新聞"
    for article in articles:
        assert isinstance(article, dict), "每則新聞應為 dict"
        assert 'title' in article, "每則新聞應包含 title 欄位"
        assert 'link' in article, "每則新聞應包含 link 欄位"
        assert article['title'], "title 不應為空"
        assert article['link'].startswith("https://meeplesherald.com/"), "link 應為 meeplesherald 網址"