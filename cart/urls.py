from django.urls import path

from . import views

urlpatterns = [
    path("cart/", views.CartList.as_view(), name="cart_list"),
    path("cart/<int:id>/", views.CartDetail.as_view(), name="cart_detail"),
]
