from django.contrib import admin

from payments.models import StripeCustomer, TransactionDetails

# Register your models here.
admin.site.register(StripeCustomer)
admin.site.register(TransactionDetails)
