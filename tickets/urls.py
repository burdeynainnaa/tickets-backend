from django.urls import path

from .views import TicketListView, TicketQRView

urlpatterns = [
    path("tickets/my/", TicketListView.as_view(), name="my-tickets"),
    path("tickets/<int:id>/qr/", TicketQRView.as_view(), name="ticket-qr"),
]
