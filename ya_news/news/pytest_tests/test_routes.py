from django.contrib.auth import SESSION_KEY
from django.urls import reverse
from http import HTTPStatus
import pytest


@pytest.mark.parametrize(
    'route_name, use_pk',
    (
        ('news:home', False),
        ('news:detail', True),
        ('users:login', False),
    )
)
def test_public_pages_availability(client, news, route_name, use_pk):
    if use_pk:
        url = reverse(route_name, kwargs={'pk': news.pk})
    else:
        url = reverse(route_name)

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    (
        'comment_edit_url',
        'comment_delete_url',
    )
)
def test_pages_availability_for_author(author_client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    (
        'comment_edit_url',
        'comment_delete_url',
    )
)
def test_pages_availability_for_reader(
    reader_client,
    request,
    url_fixture
):
    url = request.getfixturevalue(url_fixture)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_fixture',
    (
        'comment_edit_url',
        'comment_delete_url',
    )
)
def test_anonymous_user_is_redirected_to_login(client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


@pytest.mark.django_db
def test_authorized_user_can_logout(author_client):
    logout_url = reverse('users:logout')
    response = author_client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
    assert SESSION_KEY not in author_client.session
