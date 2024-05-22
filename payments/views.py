import json
from datetime import timedelta

# Create your views here.
import stripe
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from listing.models import Listing, Interested
from payments.models import StripeCustomer, TransactionDetails
from payments.serializer import StripeCustomerSerializer
from user.models import User


class StripeConfigView(APIView):
    def get(self, request):
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return Response(stripe_config)


class ProcessPaymentAPIView(APIView):
    def post(self, request, format=None):
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            listing_id = json_data.get('listing_id')
            amount = Listing.objects.get(pk=listing_id).approx_rent

            stripe.api_key = settings.STRIPE_SECRET_KEY
            domain_url = 'http://localhost:3000/'

            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + '/myinterests',
                cancel_url=domain_url + '/myinterests',
                payment_method_types=['card'],
                mode='payment',  # Change mode to 'payment' if it's not a subscription
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',  # Update currency as necessary
                            'unit_amount': amount * 100,
                            'product_data': {
                                'name': 'Your Product Name',
                                'description': 'Your Product Description',
                                # Add more product data if necessary
                            },
                        },
                        'quantity': 1,
                    }
                ],
                metadata={
                    'plan_type': "cash",
                    'listing_id': listing_id
                }
            )
            # print(checkout_session)
            return Response({'sessionId': checkout_session['id']})

        except Exception as e:
            # Handle exceptions
            return Response({'error': str(e)}, status=500)


class CreateCheckoutSessionView(APIView):
    def post(self, request):

        plan_type = request.data.get('planType')
        print("plan type", plan_type)

        domain_url = 'http://localhost:3000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:

            if plan_type == 'basic':
                price_id = settings.STRIPE_PRICE_ID_BASIC
            elif plan_type == 'premium':
                price_id = settings.STRIPE_PRICE_ID_PREMIUM
            else:
                raise ValueError('Invalid plan type')

            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'subscription',
                cancel_url=domain_url + 'subscription',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    }
                ],
                metadata={
                    'plan_type': plan_type
                }
            )
            # print(checkout_session)
            return Response({'sessionId': checkout_session['id']})
        except Exception as e:
            return Response({'error': str(e)})


class StripeWebhookView(APIView):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            print(e, "Value Error")
            return Response(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(e, "Signature")
            return Response(status=400)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            metadata = session.get('metadata', {})
            plan_type = metadata.get('plan_type')

            if plan_type == "cash":
                amount_paid = session.get('amount_total')
                amount_paid /= 100

                listing_id = metadata.get('listing_id')
                user_id = session.get('client_reference_id')  # Assuming user is authenticated
                user = User.objects.get(pk=user_id)

                interested_record = Interested.objects.filter(
                    Q(listing_id=listing_id) &
                    Q(user_id=user_id) &
                    Q(make_deal=True)
                ).first()

                interested_record.deposit_paid = True
                interested_record.save()
                # Create a new transaction instance
                new_transaction = TransactionDetails.objects.create(
                    user=user,
                    amount=amount_paid,
                    active_deposit=True,
                    timestamp=timezone.now()  # Assuming you want to timestamp the transaction with the current time
                )

            else:
                # Fetch all the required data from session
                client_reference_id = session.get('client_reference_id')
                stripe_customer_id = session.get('customer')
                stripe_subscription_id = session.get('subscription')
                amount_paid = session.get('amount_total')
                amount_paid /= 100

                # Get the user and create a new StripeCustomer
                user = User.objects.get(id=client_reference_id)
                user_name = user.name

                # Extract plan type from metadata

                # Calculate end date based on plan type
                if plan_type == 'basic':
                    days_to_add = 30
                elif plan_type == 'premium':
                    days_to_add = 60  # Adjust this value based on your premium plan duration
                else:
                    raise ValueError('Invalid plan type')

                start_date = timezone.now()
                end_date = start_date + timedelta(days=days_to_add)

                print(start_date, end_date)

                StripeCustomer.objects.create(
                    user=user,
                    stripeCustomerId=stripe_customer_id,
                    amount=int(amount_paid),
                    user_name=user_name,
                    stripeSubscriptionId=stripe_subscription_id,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True,
                )
                user.is_paid = True
                user.save()

        return Response(status=200)


class HomeView(APIView):
    def get(self, request):
        try:
            stripe_customer = StripeCustomer.objects.get(user=request.user)
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
            product = stripe.Product.retrieve(subscription.plan.product)

            return Response({
                'subscription': subscription,
                'product': product,
            })

        except StripeCustomer.DoesNotExist:
            return Response("Does not Exists")


class ActiveSubscriptionView(APIView):
    def get(self, request, format=None):
        try:
            # Retrieve active subscriptions where is_active is true
            active_subscriptions = StripeCustomer.objects.get(user=request.user, is_active=True)
            serializer = StripeCustomerSerializer(active_subscriptions)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
