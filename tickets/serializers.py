from rest_framework import serializers

from backend.serializers import EventForSerializer

from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    event = EventForSerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            "id",
            "order_id",
            "event",
            "qr_token",
            "created_at",
            "is_used",
            "used_at",
        ]
        read_only_fields = fields