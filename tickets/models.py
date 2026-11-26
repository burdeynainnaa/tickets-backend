import uuid

from django.contrib.auth.models import User
from django.db import models

from backend.models import Event
from orders.models import Order

# Create your models here.


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    qr_token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket {self.event} ({self.user})"

    def save(self, *args, **kwargs):
        if not self.qr_token:
            self.qr_token = uuid.uuid4().hex
        super().save(*args, **kwargs)
