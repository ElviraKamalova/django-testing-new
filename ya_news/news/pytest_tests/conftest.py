from datetime import timedelta
from django.test import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
    )


@pytest.fixture
def news_list(db):
    NEWS_ON_PAGE = 10
    base_date = timezone.now()
    News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text='Текст тестовой новости',
                date=base_date - timedelta(days=(NEWS_ON_PAGE - index))
            )
            for index in range(NEWS_ON_PAGE + 1)
        ]
    )
    return list(News.objects.all())


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        text='Тестовый комментарий',
        author=author,
    )


@pytest.fixture
def comments(author, news):
    now = timezone.now()

    comment1 = Comment.objects.create(news=news, author=author, text='Старый')
    Comment.objects.filter(
        pk=comment1.pk
    ).update(
        created=now - timedelta(minutes=10)
    )
    comment1.refresh_from_db()

    comment2 = Comment.objects.create(news=news, author=author, text='Новый')
    Comment.objects.filter(pk=comment2.pk).update(created=now)
    comment2.refresh_from_db()

    return (comment1, comment2)


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', kwargs={'pk': comment.pk})
