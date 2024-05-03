import tempfile

import cloudinary.uploader
from django.contrib.auth import authenticate
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from backend import settings
from .models import User, UserPreference
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserDetailsSerializer, UserProfileSerializer, \
    UserPreferenceSerializer
from .utils import verify_aadhar, validate_aadhar_text

from PIL import Image
import io


# generating jwt token from the simple-jwt
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Create your views here.

class VerifyPhoneAndSendOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_no')

        # Check if the phone number already exists in the database
        if User.objects.filter(phone_no=phone_number).exists():
            return Response({'message': 'User with this phone number already exists please Sign In'},
                            status=status.HTTP_400_BAD_REQUEST)

        # If phone number doesn't exist, proceed to send OTP using 2Factor API
        api_key = settings.TWOFACTOR_API_KEY  # Get your 2Factor API key from settings
        response = requests.get(
            'https://2factor.in/API/V1/{api_key}/SMS/+91{phone_number}/AUTOGEN3/'.format(api_key=api_key,
                                                                                         phone_number=phone_number))

        # Check if the OTP request was successful
        if response.status_code == 200:
            data = response.json()
            print(data)
            if data['Status'] == 'Success':
                return Response({'message': 'OTP sent successfully', 'Details': data['Details'], "Status": "Success"},
                                status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Failed to send OTP', "Details": data['Details']},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Failed to connect to 2Factor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # email = serializer.validated_data['email']
            # user = User.objects.get(email=email)
            # token = get_tokens_for_user(user)
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
                # image_data = profile_image.read()
                # image = Image.open(io.BytesIO(image_data))
                #
                # # Crop the image to a square
                # width, height = image.size
                # size = min(width, height)
                # left = (width - size) / 2
                # top = 0  # Start cropping from the top
                # right = (width + size) / 2
                # bottom = size
                # image = image.crop((left, top, right, bottom))
                #
                # # Resize the image to a square of desired size (optional)
                # new_size = (200, 200)
                # image = image.resize(new_size)
                #
                # # Convert the processed image back to bytes
                # output = io.BytesIO()
                # image.save(output, format='JPEG')
                # output.seek(0)
                #
                # # Upload the processed image to Cloudinary
                # upload_data = cloudinary.uploader.upload(output, folder="profile_images")

                # Process the image if it's not a URL
                upload_data = cloudinary.uploader.upload(profile_image)
                url = upload_data['url']
                user.profile_image = url
            else:
                # If 'profile_image' is a URL, directly assign it
                user.profile_image = profile_image

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
