from django.urls import path
from . import views

urlpatterns = [
    # path("pay", views.ProcessPaymentAPIView.as_view(), name="payment"),
    path('config/', views.StripeConfigView.as_view()),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view()),
    path('wallet-add/', views.ProcessPaymentAPIView.as_view()),
    path('active-subscription/', views.ActiveSubscriptionView.as_view()),
    path('webhook/', views.StripeWebhookView.as_view()),
    path('home/', views.HomeView.as_view()),
]
