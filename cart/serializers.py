import logging

from django.utils import timezone
from rest_framework import serializers

from backend.models import Event
from backend.serializers import EventForSerializer

from .models import Cart

logger = logging.getLogger(__name__)


class CartSerializer(serializers.ModelSerializer):
    event = EventForSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), source="event", write_only=True
    )
    amount = serializers.IntegerField(min_value=1, max_value=999, default=1)

    class Meta:
        model = Cart
        fields = ["id", "user_id", "event", "event_id", "amount"]
        read_only_fields = ["id", "user_id"]

    def validate_event_id(self, value):
        if value.date < timezone.now():
            logger.warning("Кошик: спроба додати минувшу подію")
            raise serializers.ValidationError("Не можна додавати минувші події в кошик")
        return value

    def create(self, data):
        user = data["user"]
        event = data["event"]
        amount = data.get("amount", 1)

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            event=event,
            defaults={"amount": amount},
        )

        if not created:
            new_amount = cart_item.amount + amount
            if new_amount > 999:
                logger.warning("Кошик: перевищено ліміт квитків")
                raise serializers.ValidationError(
                    {"amount": "Максимальні кількість квитків на одну подію - 999"}
                )
            cart_item.amount = new_amount
            cart_item.save()
        return cart_item
