from celery import Celery
from .models import StripeCustomer
from django.utils import timezone

app = Celery('tasks', broker='amqp://localhost')

@app.task
def check_and_update_subscriptions():
    today = timezone.now().date()
    subscriptions = StripeCustomer.objects.filter(end_date__date=today, is_active=True)
    for subscription in subscriptions:
        subscription.is_active = False
        subscription.save()
        print(f"Subscription for {subscription.user.username} deactivated (end date reached).")
