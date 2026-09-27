from django.contrib.auth import SESSION_KEY
from http import HTTPStatus
import pytest


@pytest.mark.parametrize(
    'client_fixture, url_fixture, expected_status',
    [
        ('client', 'home_url', HTTPStatus.OK),
        ('client', 'detail_url', HTTPStatus.OK),
        ('author_client', 'comment_edit_url', HTTPStatus.OK),
        ('author_client', 'comment_delete_url', HTTPStatus.OK),
        ('reader_client', 'comment_edit_url', HTTPStatus.NOT_FOUND),
        ('reader_client', 'comment_delete_url', HTTPStatus.NOT_FOUND),
    ],
)
def test_public_pages_availability(
    client_fixture,
    url_fixture,
    expected_status,
    request,
):
    user_client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    [
        'comment_edit_url',
        'comment_delete_url',
    ]
)
def test_anonymous_user_is_redirected_to_login(
    client,
    url_fixture,
    request,
    login_url,
):
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_authorized_user_can_logout(author_client, logout_url):
    response = author_client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
    assert SESSION_KEY not in author_client.session
