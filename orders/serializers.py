from rest_framework import serializers

from backend.serializers import EventForSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    event = EventForSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "event", "amount", "price", "subtotal"]

    def get_subtotal(self, obj):
        return obj.price * obj.amount


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user_id", "items", "total_price", "created_at"]
        read_only_fields = ["id", "user_id", "items", "total_price", "created_at"]
