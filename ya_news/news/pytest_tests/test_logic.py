from django.urls import reverse
from http import HTTPStatus
import pytest

from news.models import Comment


def test_anonymous_user_cant_create_comment(client, detail_url):
    initial_count = Comment.objects.count()
    form_data = {'text': 'Текст анонимного комментария'}
    response = client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND

    login_url = reverse('users:login')
    expected_redirect_url = f'{login_url}?next={detail_url}'
    assert response.url == expected_redirect_url

    assert Comment.objects.count() == initial_count


def test_authorized_user_can_create_comment(
        author_client,
        author,
        news,
        detail_url
):
    initial_ids = list(Comment.objects.values_list('id', flat=True))
    initial_count = Comment.objects.count()
    form_data = {'text': 'Текст комментария'}
    expected_redirect_url = f'{detail_url}#comments'

    response = author_client.post(detail_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
    assert Comment.objects.count() == initial_count + 1

    new_comments_queryset = Comment.objects.exclude(id__in=initial_ids)

    new_comment = new_comments_queryset.first()
    assert new_comments_queryset.count() == 1
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize(
    'bad_word',
    (
        'редиска',
        'негодяй',
    )
)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    initial_count = Comment.objects.count()
    form_data = {'text': f'В тексте запрещенные слова: {bad_word}.'}
    expected_error = 'Не ругайтесь!'

    response = author_client.post(detail_url, data=form_data)

    assert response.status_code == HTTPStatus.OK

    form = response.context['form']
    assert 'text' in form.errors
    assert expected_error in form.errors['text']

    assert Comment.objects.count() == initial_count


def test_author_can_edit_comment(
    author_client,
    author,
    news,
    comment,
    comment_edit_url,
    detail_url
):
    form_data = {'text': 'Обновленный текст комментария'}
    expected_redirect_url = f'{detail_url}#comments'

    comments_count_before = Comment.objects.count()

    response = author_client.post(comment_edit_url, data=form_data)

    comments_count_after = Comment.objects.count()

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
    assert comments_count_before == comments_count_after

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_comment(
    author_client,
    comment_delete_url,
    detail_url,
    comment
):
    initial_count = Comment.objects.count()
    comment_id = comment.pk

    expected_redirect_url = f'{detail_url}#comments'
    response = author_client.post(comment_delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
    assert Comment.objects.count() == initial_count - 1
    assert not Comment.objects.filter(pk=comment_id).exists()


@pytest.mark.parametrize(
    'url_fixture, data',
    [
        ('comment_edit_url', {'text': 'Изменить чужой комментарий'}),
        ('comment_delete_url', None),
    ]
)
def test_reader_cant_edit_or_delete_comment(
    reader_client,
    comment,
    url_fixture,
    data,
    request
):
    url = request.getfixturevalue(url_fixture)
    response = reader_client.post(url, data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    if data:
        assert not Comment.objects.filter(
            pk=comment.pk,
            text=data['text']).exists()
    else:
        assert Comment.objects.filter(pk=comment.pk).exists()
