from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from cart.models import Cart
from orders.models import Order
from tickets.models import Ticket
from tickets.services import generate_qr_png


def authenticate_client(api_client, username="user", password="1234"):
    tokens = api_client.post(
        "/api/auth/login/",
        {"username": username, "password": password},
        format="json",
    )
    access_token = tokens.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


@pytest.mark.django_db
def test_generate_qr_png_returns_valid_png_bytes():
    png_bytes = generate_qr_png("test-qr-token-123")
    assert isinstance(png_bytes, bytes)
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.django_db
def test_create_order_generates_tickets_with_unique_qr_tokens(api_client, user, event):
    Cart.objects.create(user=user, event=event, amount=3)
    authenticate_client(api_client)
    response = api_client.post("/api/orders/", format="json")
    tickets = Ticket.objects.filter(user=user, event=event)
    qr_tokens = list((tickets.values_list("qr_token")))
    assert response.status_code == 201
    assert tickets.count() == 3
    assert len(set(qr_tokens)) == 3


@pytest.mark.django_db
def test_get_my_tickets_no_authorization(api_client):
    response = api_client.get("/api/tickets/my/", format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_my_tickets(api_client, user, event):
    order = Order.objects.create(user=user, total_price=Decimal("500.00"))
    Ticket.objects.create(order=order, event=event, user=user, qr_token="token-user")
    authenticate_client(api_client)
    response = api_client.get("/api/tickets/my/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_my_tickets_returns_only_own_tickets(api_client, user, event):
    user2 = User.objects.create_user(username="user2", password="1234")
    order1 = Order.objects.create(user=user, total_price=Decimal("500.00"))
    ticket1 = Ticket.objects.create(
        order=order1, user=user, event=event, qr_token="token-user-1"
    )
    order2 = Order.objects.create(user=user2, total_price=Decimal("500.00"))
    Ticket.objects.create(
        order=order2, user=user2, event=event, qr_token="token-user-2"
    )
    authenticate_client(api_client)
    response = api_client.get("/api/tickets/my/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == ticket1.id
    assert response.data[0]["qr_token"] == "token-user-1"


@pytest.mark.django_db
def test_get_ticket_qr_no_authorization(api_client, user, event):
    order = Order.objects.create(user=user, total_price=Decimal("500.00"))
    ticket = Ticket.objects.create(
        order=order, user=user, event=event, qr_token="token-unauth"
    )
    response = api_client.get(f"/api/tickets/{ticket.id}/qr/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_ticket_qr(api_client, user, event):
    order = Order.objects.create(user=user, total_price=Decimal("500.00"))
    ticket = Ticket.objects.create(
        order=order, user=user, event=event, qr_token="token-valid-png"
    )
    authenticate_client(api_client)
    response = api_client.get(f"/api/tickets/{ticket.id}/qr/")
    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.django_db
def test_get_invalid_ticket_qr(api_client, user, event):
    order = Order.objects.create(user=user, total_price=Decimal("500.00"))
    Ticket.objects.create(
        order=order, user=user, event=event, qr_token="token-valid-png"
    )
    authenticate_client(api_client)
    response = api_client.get("/api/tickets/999/qr/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_other_user_ticket_qr(api_client, user, event):
    user2 = User.objects.create_user(username="user2", password="1234")
    order2 = Order.objects.create(user=user2, total_price=Decimal("500.00"))
    other_ticket = Ticket.objects.create(
        order=order2, user=user2, event=event, qr_token="token-other-user"
    )

    authenticate_client(api_client)
    response = api_client.get(f"/api/tickets/{other_ticket.id}/qr/")
    assert response.status_code == 404
