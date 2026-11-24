from django.db import models
from django.contrib.auth.models import User
from backend.models import Event
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="cart_items")
    amount = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(999)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_cart",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.event} (x{self.amount})"
