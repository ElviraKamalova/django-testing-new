NEWS_ON_PAGE = 10


def test_homepage_news_count_and_order(client, news_list, home_url):
    response = client.get(home_url)
    news_in_context = list(response.context['news_list'])
    assert len(news_in_context) == NEWS_ON_PAGE

    context_dates = [news.date for news in news_in_context]

    all_dates = [news.date for news in news_list]
    expected_dates = sorted(all_dates, reverse=True)[:NEWS_ON_PAGE]
    assert context_dates == expected_dates


def test_comments_order_on_detail_page(
        client,
        news,
        comments,
        detail_url
):
    comment1, comment2 = comments
    response = client.get(detail_url)
    news_obj = response.context['news']
    comments_in_context = list(news_obj.comment_set.order_by('created'))
    assert comments_in_context == [comment1, comment2]


def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_user_has_comment_form(detail_url, author_client):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    form = response.context['form']
    assert hasattr(form, 'fields')
