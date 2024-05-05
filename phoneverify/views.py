from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from phone_verify.api import VerificationViewSet
from phone_verify import serializers as phone_serializers

from user.models import User


class YourCustomViewSet(VerificationViewSet):

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def verify_and_register(self, request):
        """Function to verify phone number and register a user"""

        phone_number = request.data.get(
            'phone_number')  # Assuming 'phone_number' is the field name in your request data

        print("phone no", phone_number)

        cleaned_phone_number = phone_number[3:]

        if User.objects.filter(phone_no=cleaned_phone_number).exists():
            return Response({"error": "Phone number already exists"}, status=400)

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If the phone number doesn't exist, continue with your registration process
        # You can add your custom registration logic here
        # For example:
        # user = User.objects.create(phone_number=phone_number)

        # Assuming you want to return a success response
        return Response(serializer.data, status=status.HTTP_200_OK)
