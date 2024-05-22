import tempfile

import cloudinary.uploader
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserPreference
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserDetailsSerializer, UserProfileSerializer, \
    UserPreferenceSerializer, ContactSerializer, UserPasswordResetEmailSerializer, UserPasswordResetSerializer
from .utils import verify_aadhar, validate_aadhar_text


# generating jwt token from the simple-jwt
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Create your views here.

class RegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            refresh_token = RefreshToken.for_user(user)
            return Response({"tokens": {"refresh": str(refresh_token), "access": str(refresh_token.access_token)},
                             "message": "registration successfull"},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(email=email, password=password)

            if user is not None:
                refresh_token = RefreshToken.for_user(user)
                user_serializer = UserDetailsSerializer(user)  # Serialize user details without password
                return Response(
                    {"tokens": {"refresh": str(refresh_token), "access": str(refresh_token.access_token)},
                     "message": "Login success", "data": user_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': "Email password not valid"},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetEmailView(APIView):
    def post(self, request, format=None):

        serializer = UserPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"Message": "Reset password email has been sent to you"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    def post(self, request, uid, token, format=None):
        serializers = UserPasswordResetSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializers.is_valid():
            return Response(
                {"Message": "Password reset successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDataView(APIView):
    def get(self, request, pk):
        user_data = User.objects.get(pk=pk)
        print(user_data)
        serializer = UserDetailsSerializer(user_data)
        return Response(serializer.data, status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        user_data = User.objects.get(pk=user_id)
        serializer = UserProfileSerializer(user_data)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request):
        user_id = request.user.id
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        new_email = data.get("email")
        if new_email and new_email != user.email:
            # Check if the new email already exists in the database
            if User.objects.exclude(pk=user_id).filter(email=new_email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # data = request.data
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        user.phone_no = data.get("phone_no", user.phone_no)
        user.bio = data.get("bio", user.bio)
        user.occupation = data.get("occupation", user.occupation)
        user.gender = data.get("gender", user.gender)
        user.age = data.get("age", user.age)

        if 'profile_image' in request.data:
            profile_image = request.data.get('profile_image')
            if isinstance(profile_image, InMemoryUploadedFile):
                # Process the image if it's not a URL
                upload_data = cloudinary.uploader.upload(profile_image)
                url = upload_data['url']
                user.profile_image = url

        user.save()

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class UserPreferenceAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            user_preferences = UserPreference.objects.get(user_id=user_id)
            serializer = UserPreferenceSerializer(user_preferences)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserPreference.DoesNotExist:
            return Response({"message": "User preferences not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        print(request.data)
        serializer = UserPreferenceSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()

            return Response({"message": "User preferences added."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        try:
            instance = UserPreference.objects.get(user=request.user)
        except UserPreference.DoesNotExist:
            return Response("User preferences not found", status=status.HTTP_404_NOT_FOUND)

        serializer = UserPreferenceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Your Prefernce Updated Successfully", "Data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AadharVerificationView(APIView):
    def post(self, request):

        aadhar = request.FILES.get('aadhar')

        user_id = request.user.id
        user = User.objects.get(pk=user_id)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in aadhar.chunks():
                temp_file.write(chunk)

        # Get the path of the saved image file
        image_path = temp_file.name

        # Check the image for text
        is_text_present = verify_aadhar(image_path)
        print(is_text_present)
        name_present, aadhar_number_valid = validate_aadhar_text(is_text_present, user.name)

        is_verified = False
        if name_present and aadhar_number_valid:
            is_verified = True
        if is_verified:
            user.is_verified = True
            user.save()
            return Response({"is_verified": is_verified}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Upload Valid Aaadhar According to Instructions"},
                            status=status.HTTP_400_BAD_REQUEST)


class ContactFormAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Thank you for the contact"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
