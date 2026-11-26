import logging
import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from tickets.models import Ticket

from .models import Order, OrderItem
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)


class OrderList(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Переглянути історію замовлень авторизованого користувача",
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, request):
        logger.debug("Користувач id=%s запитує історію замовлень", request.user.id)
        orders = Order.objects.filter(user=request.user).prefetch_related(
            "items__event"
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Створити замовлення на основі кошика",
        request=None,
        responses={201: OrderSerializer, 400: dict},
    )
    def post(self, request):
        cart_items = list(
            Cart.objects.filter(user=request.user).select_related("event")
        )
        if not cart_items:
            logger.warning(
                "Користувач id=%s намагався оформити замовлення з порожнім кошиком",
                request.user.id,
            )
            return Response(
                {
                    "error": "Кошик порожній. Додайте квитки перед оформленням замовлення."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        for item in cart_items:
            if item.event.date < now:
                logger.warning(
                    "Користувач id=%s має минулу подію id=%s у кошику",
                    request.user.id,
                    item.event.id,
                )
                return Response(
                    {
                        "error": f"Подія «{item.event.title}» вже минула. Видаліть її з кошика."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        total_price = sum(
            (item.event.price * item.amount for item in cart_items),
            Decimal("0.00"),
        )

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
            )
            order_items = [
                OrderItem(
                    order=order,
                    event=item.event,
                    amount=item.amount,
                    price=item.event.price,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            tickets = [
                Ticket(
                    order=order,
                    event=item.event,
                    user=request.user,
                    qr_token=uuid.uuid4().hex,
                )
                for item in cart_items
                for i in range(item.amount)
            ]
            Ticket.objects.bulk_create(tickets)

            Cart.objects.filter(user=request.user).delete()

        order = Order.objects.prefetch_related("items__event").get(id=order.id)
        logger.info(
            "Користувач id=%s оформив замовлення id=%s (сума=%s, позицій=%s, квитків=%s)",
            request.user.id,
            order.id,
            order.total_price,
            len(order_items),
            len(tickets),
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
