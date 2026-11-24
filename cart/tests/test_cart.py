import pytest
from datetime import timedelta
from django.utils import timezone
from cart.models import Cart
from django.contrib.auth.models import User
from backend.models import Event

@pytest.mark.django_db
def test_get_cart_no_authorization(api_client):
    response = api_client.get("/api/cart/", format="json")
    assert response.status_code == 401

@pytest.mark.django_db
def test_get_empty_cart(api_client, user):
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.get(f"/api/cart/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 0

@pytest.mark.django_db
def test_get_cart_with_item(api_client, user, event):
    Cart.objects.create(user=user, event=event, amount=3)
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.get(f"/api/cart/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["amount"] == 3
    assert response.data[0]["event"]["id"] == event.id

@pytest.mark.django_db
def test_get_cart_returns_only_own_items(api_client, user, event):
    user2 = User.objects.create_user(username="user2", password="1234")
    Cart.objects.create(user=user, event=event, amount=3)
    Cart.objects.create(user=user2, event=event, amount=1)
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.get(f"/api/cart/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["amount"] == 3
    assert response.data[0]["event"]["id"] == event.id

@pytest.mark.django_db
def test_add_to_cart_no_authorization(api_client,event):
    response = api_client.post("/api/cart/", {"event_id": event.id, "amount": 1}, format="json")
    assert response.status_code == 401

@pytest.mark.django_db
def test_add_to_cart(api_client, event, user):
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.post("/api/cart/", {"event_id": event.id, "amount": 1}, format="json")
    assert response.status_code == 201
    assert response.data["amount"] == 1
    assert response.data["event"]["id"] == event.id
    assert Cart.objects.filter(user=user, event=event).count() == 1

@pytest.mark.django_db
def test_add_same_event_to_cart_sums_amount(api_client, user, event):
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    api_client.post("/api/cart/", {"event_id": event.id, "amount": 1}, format="json")
    response = api_client.post("/api/cart/", {"event_id": event.id, "amount": 1}, format="json")
    assert response.status_code == 201
    assert response.data["amount"] == 2
    assert response.data["event"]["id"] == event.id
    assert Cart.objects.filter(user=user, event=event).count() == 1

@pytest.mark.django_db
def test_add_to_cart_with_invalid_amount(api_client, user, event):
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = api_client.post("/api/cart/", {"event_id": event.id, "amount": -99}, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_add_to_cart_exceeds_max_amount(api_client, user, event):
    Cart.objects.create(user=user, event=event, amount=998)
    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.post("/api/cart/", {"event_id": event.id, "amount": 10}, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_add_past_event_to_cart(api_client, user, event):
    past_event = Event.objects.create(
        title = "Past",
        price = "300.00",
        date = timezone.now() - timedelta(days=7),
        category = event.category,
        artist = event.artist,
        venue = event.venue,
    )

    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.post("/api/cart/", {"event_id": past_event.id, "amount": 10}, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_delete_cart_item(api_client, user, event):
    cart_item = Cart.objects.create(user=user, event=event, amount = 1)

    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.delete(f"/api/cart/{cart_item.id}/", format="json")
    assert response.status_code == 204

@pytest.mark.django_db
def test_delete_invalid_cart_item(api_client, user, event):
    cart_item = Cart.objects.create(user=user, event=event, amount = 1)

    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.delete("/api/cart/999/", format="json")
    assert response.status_code == 404

@pytest.mark.django_db
def test_delete_cart_item_no_authorization(api_client, user, event):
    cart_item = Cart.objects.create(user=user, event=event, amount = 1)
    response = api_client.delete(f"/api/cart/{cart_item.id}/", format="json")
    assert response.status_code == 401

@pytest.mark.django_db
def test_delete_other_user_cart_item(api_client, user, event):
    user2 = User.objects.create_user(username="user2", password="1234")
    cart_item_user2 = Cart.objects.create(user=user2, event=event, amount=1)

    login_url = "/api/auth/login/"
    tokens = api_client.post(
        login_url,
        {
            "username": "user",
            "password": "1234",
        },
        format="json",
    )

    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = api_client.delete(f"/api/cart/{cart_item_user2.id}/", format="json")
    assert response.status_code == 403
