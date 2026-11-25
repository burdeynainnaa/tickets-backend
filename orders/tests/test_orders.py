from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from backend.models import Event
from cart.models import Cart
from orders.models import Order, OrderItem


def authenticate_client(api_client, username="user", password="1234"):
    tokens = api_client.post(
        "/api/auth/login/",
        {"username": username, "password": password},
        format="json",
    )
    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


@pytest.mark.django_db
def test_get_orders_no_authorization(api_client):
    response = api_client.get("/api/orders/", format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_order_no_authorization(api_client):
    response = api_client.post("/api/orders/", format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_order_empty_cart(api_client, user):
    authenticate_client(api_client)
    response = api_client.post("/api/orders/", format="json")
    assert response.status_code == 400
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_create_order_with_past_event_in_cart(api_client, user, event):
    past_event = Event.objects.create(
        title="Past Event",
        price=Decimal("250.00"),
        date=timezone.now() - timedelta(days=2),
        category=event.category,
        artist=event.artist,
        venue=event.venue,
    )
    Cart.objects.create(user=user, event=past_event, amount=2)

    authenticate_client(api_client)
    response = api_client.post("/api/orders/", format="json")
    assert response.status_code == 400
    assert Order.objects.count() == 0
    assert Cart.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_create_order_success_and_clears_cart(api_client, user, event):
    Cart.objects.create(user=user, event=event, amount=2)

    authenticate_client(api_client)
    response = api_client.post("/api/orders/", format="json")

    assert response.status_code == 201
    assert Decimal(response.data["total_price"]) == Decimal(str(event.price)) * 2
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["amount"] == 2
    assert response.data["items"][0]["event"]["id"] == event.id
    assert Cart.objects.filter(user=user).count() == 0
    assert Order.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_get_orders_returns_only_own_orders(api_client, user, event):
    user2 = User.objects.create_user(username="user2", password="1234")

    order1 = Order.objects.create(user=user, total_price=Decimal("500.00"))
    OrderItem.objects.create(
        order=order1, event=event, amount=1, price=Decimal("500.00")
    )

    order2 = Order.objects.create(user=user2, total_price=Decimal("1000.00"))
    OrderItem.objects.create(
        order=order2, event=event, amount=2, price=Decimal("500.00")
    )

    authenticate_client(api_client)
    response = api_client.get("/api/orders/", format="json")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == order1.id
