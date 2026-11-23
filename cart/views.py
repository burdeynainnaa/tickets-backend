from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart
from .serializers import CartSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class CartList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"Користувач id={request.user.id} запитує свій кошик")
        items = Cart.objects.filter(user=request.user).select_related("event")
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(user=request.user)
        logger.info(f"Користувач id={request.user.id} додав у кошик подію id={item.event.id} (amount={item.amount})")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class CartDetail(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        item = get_object_or_404(Cart, id=id)
        if item.user != request.user:
            logger.warning(f"користувач id={request.user.id} намагався видалити позицію кошика id={id}")
            return Response({"error": "Ви не маєте прав видаляти цю позицію з кошика"}, status=status.HTTP_403_FORBIDDEN)
        
        item.delete()
        logger.info(f"Користувач id={request.user.id} видалив позицію кошика id={id}")
        return Response(status=status.HTTP_204_NO_CONTENT)