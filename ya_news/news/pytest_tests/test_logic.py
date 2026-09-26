from http import HTTPStatus
import pytest

from news.models import Comment


def test_anonymous_user_cant_create_comment(client, detail_url):
    initial_count = Comment.objects.count()
    form_data = {'text': 'Текст анонимного комментария'}
    response = client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count


def test_authorized_user_can_create_comment(
        author_client,
        author,
        news,
        detail_url
):
    initial_count = Comment.objects.count()
    form_data = {'text': 'Текст комментария'}
    expected_redirect_url = detail_url + '#comments'

    response = author_client.post(detail_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
    assert Comment.objects.count() == initial_count + 1

    new_comment = Comment.objects.latest('id')
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
    expected_redirect_url = detail_url + '#comments'

    response = author_client.post(comment_edit_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url

    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_comment(
    author_client,
    comment_delete_url,
    detail_url
):
    initial_count = Comment.objects.count()
    expected_redirect_url = detail_url + '#comments'

    response = author_client.post(comment_delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url

    assert Comment.objects.count() == initial_count - 1


def test_reader_cant_edit_comment(
    reader_client,
    comment,
    comment_edit_url
):
    form_data = {'text': 'Изменить чужой комментарий'}

    response = reader_client.post(comment_edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text != form_data['text']


def test_reader_cant_delete_comment(
    reader_client,
    comment_delete_url
):
    initial_count = Comment.objects.count()
    response = reader_client.post(comment_delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
