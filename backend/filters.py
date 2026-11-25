from datetime import datetime, time, timedelta
from datetime import timezone as dt_timezone

import django_filters
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.exceptions import ValidationError

from .models import Artist, Event, Venue

INVALID_DATE_MSG = (
    "Введіть коректну дату або дату й час "
    "(наприклад, 2026-11-20 або 2026-11-20T19:00:00Z)."
)


class EventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    price = django_filters.NumberFilter(field_name="price", lookup_expr="exact")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    date_from = django_filters.CharFilter(method="filter_date_from")
    date_to = django_filters.CharFilter(method="filter_date_to")

    category = django_filters.NumberFilter(
        field_name="category_id", lookup_expr="exact"
    )
    category_name = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    artist = django_filters.NumberFilter(field_name="artist_id", lookup_expr="exact")
    artist_name = django_filters.CharFilter(
        field_name="artist__name", lookup_expr="icontains"
    )
    venue = django_filters.NumberFilter(field_name="venue_id", lookup_expr="exact")
    venue_name = django_filters.CharFilter(
        field_name="venue__name", lookup_expr="icontains"
    )
    city = django_filters.CharFilter(
        field_name="venue__city",
        lookup_expr="icontains",
        method="filter_city",
    )

    def filter_city(self, queryset, name, value):
        cleaned = value.strip()
        if not cleaned:
            return queryset
        return queryset.filter(**{f"{name}__icontains": cleaned})

    def _to_utc(self, dt: datetime) -> datetime:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt.astimezone(dt_timezone.utc)

    def _parse_bound(self, raw_value: str, is_end: bool):
        value = raw_value.strip()

        try:
            d = parse_date(value)
            dt = parse_datetime(value) if d is None else None
        except ValueError as exc:
            raise ValidationError(INVALID_DATE_MSG) from exc

        if d is not None:
            target_date = d + timedelta(days=1) if is_end else d
            naive_dt = datetime.combine(target_date, time.min)
            return self._to_utc(naive_dt), is_end

        if dt is not None:
            return self._to_utc(dt), False

        raise ValidationError(INVALID_DATE_MSG)

    def filter_date_from(self, queryset, name, value):
        if not str(value).strip():
            return queryset
        dt, _ = self._parse_bound(str(value), is_end=False)
        return queryset.filter(date__gte=dt)

    def filter_date_to(self, queryset, name, value):
        if not str(value).strip():
            return queryset
        dt, is_date_only = self._parse_bound(str(value), is_end=True)
        if is_date_only:
            return queryset.filter(date__lt=dt)
        return queryset.filter(date__lte=dt)

    class Meta:
        model = Event
        fields = [
            "title",
            "price",
            "min_price",
            "max_price",
            "date_from",
            "date_to",
            "category",
            "category_name",
            "artist",
            "artist_name",
            "venue",
            "venue_name",
            "city",
        ]


class ArtistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    class Meta:
        model = Artist
        fields = ["name", "description"]


class VenueFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    city = django_filters.CharFilter(
        field_name="city",
        lookup_expr="icontains",
        method="filter_city",
    )
    address = django_filters.CharFilter(field_name="address", lookup_expr="icontains")

    def filter_city(self, queryset, name, value):
        cleaned = value.strip()
        if not cleaned:
            return queryset
        return queryset.filter(**{f"{name}__icontains": cleaned})

    class Meta:
        model = Venue
        fields = ["name", "city", "address"]
