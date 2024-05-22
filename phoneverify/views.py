from phone_verify import serializers as phone_serializers
from phone_verify.api import VerificationViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from user.models import User


class YourCustomViewSet(VerificationViewSet):

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def verify_and_register(self, request):
        """Function to verify phone number and register a user"""
        print("Hello")
        phone_number = request.data.get(
            'phone_number')

        if User.objects.filter(phone_no=phone_number).exists():
            return Response({"error": "Phone number already exists"}, status=400)

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.id is not None:
            user_id = request.user.id
            print("----------", user_id)
            user = User.objects.get(pk=user_id)
            user.phone_no = phone_number
            user.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
