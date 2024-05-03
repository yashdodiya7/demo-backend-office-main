from datetime import timezone

from django.db import models
from user.models import User


# Create your models here.
class StripeCustomer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    amount = models.IntegerField()
    user_name = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name


class TransactionDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active_deposit = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # description = models.TextField()  # Description of the transaction
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the transaction

    def __str__(self):
        return f"{self.user.name} - {self.amount}"
