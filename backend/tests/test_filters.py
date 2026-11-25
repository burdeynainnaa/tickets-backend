from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from backend.models import Artist, Category, Event, Venue

EVENTS_URL = "/api/events/"
ARTISTS_URL = "/api/artists/"
VENUES_URL = "/api/venues/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def seed_data():
    now = timezone.now().replace(hour=18, minute=0, second=0, microsecond=0)
    cat_concert = Category.objects.create(name="Концерт")
    cat_theater = Category.objects.create(name="Театр")

    artist_rock = Artist.objects.create(
        name="Океан Ельзи", description="Український рок-гурт"
    )
    artist_jazz = Artist.objects.create(
        name="Jazz Quartet", description="Вечірній джаз"
    )

    venue_kyiv = Venue.objects.create(
        name="Палац Спорту",
        description="Головна арена",
        city="Kyiv",
        address="Спортивна площа, 1",
    )
    venue_lviv = Venue.objects.create(
        name="Оперний театр",
        description="Історична сцена",
        city="Lviv",
        address="Проспект Свободи, 28",
    )

    event_1 = Event.objects.create(
        title="Великий Концерт у Києві",
        description="Живий звук",
        price=Decimal("500.00"),
        date=now + timedelta(days=2),
        category=cat_concert,
        artist=artist_rock,
        venue=venue_kyiv,
    )
    event_2 = Event.objects.create(
        title="Камерний Джаз",
        description="Акустичний сет",
        price=Decimal("1500.00"),
        date=now + timedelta(days=10),
        category=cat_theater,
        artist=artist_jazz,
        venue=venue_lviv,
    )

    return {
        "now": now,
        "cat_concert": cat_concert,
        "cat_theater": cat_theater,
        "artist_rock": artist_rock,
        "artist_jazz": artist_jazz,
        "venue_kyiv": venue_kyiv,
        "venue_lviv": venue_lviv,
        "event_1": event_1,
        "event_2": event_2,
    }


@pytest.mark.django_db
def test_event_filter_by_city_partial_and_whitespace(api_client, seed_data):
    res = api_client.get(EVENTS_URL, {"city": "  kyi  "})
    assert res.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in res.data]
    assert titles == ["Великий Концерт у Києві"]


@pytest.mark.django_db
def test_event_filter_by_price_range_and_relations(api_client, seed_data):
    res = api_client.get(
        EVENTS_URL,
        {
            "min_price": "400",
            "max_price": "800",
            "artist_name": "Ельзи",
            "venue_name": "Спорту",
            "category_name": "Концерт",
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 1
    assert res.data[0]["id"] == seed_data["event_1"].id


@pytest.mark.django_db
def test_event_filter_by_date_only_and_iso_datetime(api_client, seed_data):
    target_day = timezone.localtime(seed_data["event_1"].date).date().isoformat()
    res_date = api_client.get(
        EVENTS_URL, {"date_from": target_day, "date_to": target_day}
    )
    assert res_date.status_code == status.HTTP_200_OK
    assert [item["id"] for item in res_date.data] == [seed_data["event_1"].id]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"min_price": "not-a-number"},
        {"max_price": "abc"},
        {"price": "invalid"},
        {"category": "invalid-id"},
        {"artist": "invalid-id"},
        {"venue": "invalid-id"},
        {"date_from": "not-a-date"},
        {"date_to": "2026-99-99"},
    ],
)
def test_event_filter_invalid_params_return_400(api_client, seed_data, params):
    res = api_client.get(EVENTS_URL, params)
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_artist_filter_positive_and_negative(api_client, seed_data):
    res_ok = api_client.get(ARTISTS_URL, {"name": "quartet", "description": "джаз"})
    assert res_ok.status_code == status.HTTP_200_OK
    assert len(res_ok.data) == 1
    assert res_ok.data[0]["id"] == seed_data["artist_jazz"].id

    res_cyr = api_client.get(
        ARTISTS_URL, {"name": "Ельзи", "description": "Український рок-гурт"}
    )
    assert res_cyr.status_code == status.HTTP_200_OK
    assert len(res_cyr.data) == 1
    assert res_cyr.data[0]["id"] == seed_data["artist_rock"].id

    res_empty = api_client.get(ARTISTS_URL, {"name": "неіснуючий-артист"})
    assert res_empty.status_code == status.HTTP_200_OK
    assert res_empty.data == []


@pytest.mark.django_db
def test_venue_filter_positive_and_negative(api_client, seed_data):
    res_ok = api_client.get(VENUES_URL, {"city": "  lvi ", "address": "Свободи"})
    assert res_ok.status_code == status.HTTP_200_OK
    assert len(res_ok.data) == 1
    assert res_ok.data[0]["id"] == seed_data["venue_lviv"].id

    res_empty = api_client.get(VENUES_URL, {"city": "НеіснуючеМісто"})
    assert res_empty.status_code == status.HTTP_200_OK
    assert res_empty.data == []
