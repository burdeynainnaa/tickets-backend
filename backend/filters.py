import django_filters

from .models import Artist, Event, Venue


class EventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    price = django_filters.NumberFilter(field_name="price", lookup_expr="exact")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    date_from = django_filters.IsoDateTimeFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.IsoDateTimeFilter(field_name="date", lookup_expr="lte")

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
    city = django_filters.CharFilter(field_name="venue__city", lookup_expr="iexact")

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
    city = django_filters.CharFilter(field_name="city", lookup_expr="iexact")
    address = django_filters.CharFilter(field_name="address", lookup_expr="icontains")

    class Meta:
        model = Venue
        fields = ["name", "city", "address"]
