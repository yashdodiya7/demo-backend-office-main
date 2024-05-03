from rest_framework import serializers
from .models import StripeCustomer


class StripeCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeCustomer
        fields = ['amount', 'user_name', 'start_date', 'end_date', 'is_active']
