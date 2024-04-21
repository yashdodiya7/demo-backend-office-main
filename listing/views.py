import os
import tempfile
from copy import deepcopy

import cloudinary.uploader
from django.db.models import Q
from django.shortcuts import render
from rest_framework.generics import get_object_or_404

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # Require authentication
from rest_framework import status, generics
from .models import Listing, Amenities, Highlight  # Import all models
from .serializers import ListingSerializer, ListingCreateSerializer, \
    GetAllListDataSerializer, GetAllListUserNotLoginSerializer, ListingNearbySerializer  # Import your ListingSerializer
from user.models import User
from .utils import check_image_for_text, calculate_distance
from user.serializers import UserProfileSerializer


class ListingSearchAPIView(APIView):
    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return GetAllListDataSerializer
        else:
            return GetAllListUserNotLoginSerializer

    def get(self, request):
        user_name = request.query_params.get('user_name', '')
        occupation = request.query_params.get('occupation', '')
        user_latitude = request.query_params.get('user_latitude')
        user_longitude = request.query_params.get('user_longitude')

        # Filter queryset based on user_name and occupation
        queryset = Listing.objects.all()
        filter_conditions = Q()
        if user_name:
            filter_conditions |= Q(user__name__icontains=user_name)
        if occupation:
            filter_conditions |= Q(user__occupation__icontains=occupation)
        if filter_conditions:
            queryset = queryset.filter(filter_conditions)

        # Exclude listings created by the authenticated user
        if request.user.is_authenticated:
            queryset = queryset.exclude(user=request.user)

        # Serialize queryset and return response
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True, context={"request": request, "user_latitude": user_latitude,
                                                                    "user_longitude": user_longitude})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllListings(APIView):
    def post(self, request):
        user_id = request.user.id if request.user.is_authenticated else None

        user_latitude = request.data.get('user_latitude')
        user_longitude = request.data.get('user_longitude')

        if user_id:
            listings = Listing.objects.exclude(Q(user=request.user) | Q(is_available=False))
            serializer = GetAllListDataSerializer(listings, many=True,
                                                  context={'request': request, 'user_latitude': user_latitude,
                                                           'user_longitude': user_longitude})
        else:
            listings = Listing.objects.filter(is_available=True)
            serializer = GetAllListUserNotLoginSerializer(listings, many=True, context={
                'user_latitude': user_latitude,
                'user_longitude': user_longitude
            })

        if listings.exists():  # Check if the queryset is not empty
            return Response(serializer.data)
        else:
            return Response({"message": "No listings found"}, status=status.HTTP_204_NO_CONTENT)


class CreateListingView(APIView):
    permission_classes = [IsAuthenticated]  # Allow only authenticated users
    def post(self, request):

        if request.user.is_host and Listing.objects.filter(user=request.user, is_available=True).exists():
            return Response({"message": "You cannot create another post as you already have an available post"},
                            status=status.HTTP_400_BAD_REQUEST)

        images = request.data.getlist('images')  # Get list of InMemoryUploadedFile objects
        image_urls = []
        for image in images:

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)

            # Get the path of the saved image file
            image_path = temp_file.name

            # Check the image for text
            is_text_present = check_image_for_text(image_path)

            if is_text_present:
                # Delete the temporary file
                os.remove(image_path)
                return Response({"message": "You can not upload image with Address or Number"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                upload_data = cloudinary.uploader.upload(image_path)
                url = upload_data['url']
                image_urls.append(url)

        json_data = {}
        for key, value in request.data.items():
            if isinstance(value, list) and len(value) == 1:
                json_data[key] = value[0]
            elif key in ['amenities', 'highlights']:
                json_data[key] = [int(item.strip()) for item in value[1:-1].split(',')]
            else:
                json_data[key] = value

        json_data['user'] = request.user.id
        json_data['image_urls'] = image_urls

        # make a is_available post
        json_data['is_available'] = True

        serializer = ListingCreateSerializer(data=json_data)
        if serializer.is_valid():
            serializer.save()

            request.user.is_host = True
            request.user.save()

            return Response({"message": "Post Created", "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetSingleListing(APIView):
    def get(self, request, listId):
        listing = Listing.objects.get(pk=listId)
        # user_id = request.user.id if request.user.is_authenticated else None
        serializer = ListingSerializer(listing)
        return Response(serializer.data)

class GetUpdateListingView(APIView):
    # permission_classes = [IsAuthenticated]  # Allow only authenticated users
    def get(self, request):
        listing = Listing.objects.get(Q(user=request.user.id) & Q(is_available=True))
        # user_id = request.user.id if request.user.is_authenticated else None
        serializer = ListingSerializer(listing)
        return Response(serializer.data)

    def patch(self, request):
        user_id = request.user.id
        try:
            listing = Listing.objects.get(Q(user=user_id) & Q(is_available=True))
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the host and the listing is available
        if request.user.is_host and request.user == listing.user and listing.is_available:
            # Update the listing data
            for key, value in request.data.items():
                if key == 'images':
                    image_urls = []
                    for image in request.FILES.getlist('images'):
                        upload_data = cloudinary.uploader.upload(image)
                        url = upload_data['url']
                        image_urls.append(url)
                    setattr(listing, 'image_urls', image_urls)
                elif key in ['amenities', 'highlights']:
                    # Clear existing values and set new values for many-to-many fields
                    getattr(listing, key).clear()  # Clear existing values
                    getattr(listing, key).set([int(item.strip()) for item in value[1:-1].split(',')])  # Set new values
                else:
                    setattr(listing, key, value)
            listing.save()

            # Serialize the updated listing and return the response
            serializer = ListingSerializer(listing, context={'request': request})
            return Response({"message": "Post Updated"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You are not authorized to update this listing'}, status=status.HTTP_403_FORBIDDEN)


class NearbyPostsAPIView(APIView):
    def get(self, request, listId):
        # Get the current post object
        current_post = get_object_or_404(Listing, pk=listId)

        # Fetch nearby posts based on the current post's location
        nearby_posts = Listing.objects.exclude(pk=listId)

        # Serialize the nearby posts
        serializer = ListingNearbySerializer(nearby_posts, many=True)

        return Response(serializer.data)


class UserListProfileView(APIView):
    def get(self, request, listId):
        try:
            # Retrieve the listing based on the provided ListId
            listing = Listing.objects.get(id=listId)

            # Retrieve the user associated with the listing
            user = listing.user

            # Serialize the user data
            serializer = UserProfileSerializer(user)

            # Return the serialized user profile
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Listing.DoesNotExist:
            return Response({"message": "Listing does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
