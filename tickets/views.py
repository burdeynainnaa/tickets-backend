import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ticket
from .serializers import TicketSerializer
from .services import generate_qr_png

# Create your views here.

logger = logging.getLogger(__name__)


class TicketListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Переглянути куплені квитки авторизованого користувача",
        responses={200: TicketSerializer(many=True)},
    )
    def get(self, request):
        logger.debug(f"Користувач id={request.user.id} запитує список своїх квитків")
        tickets = (
            Ticket.objects.filter(user=request.user)
            .select_related("event", "order")
            .order_by("-created_at")
        )
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class TicketQRView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Отримати PNG-зображення QR-коду для квитка",
        responses={(200, "image/png"): bytes, 404: dict},
    )
    def get(self, request, id):
        ticket = get_object_or_404(Ticket, id=id, user=request.user)
        logger.debug(
            f"Користувач id={request.user.id} генерує QR-код для квитка id={ticket.id}"
        )
        png_bytes = generate_qr_png(ticket.qr_token)
        return HttpResponse(png_bytes, content_type="image/png")
