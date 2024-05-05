import os
import tempfile
from copy import deepcopy

import cloudinary.uploader
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render
from rest_framework.generics import get_object_or_404

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # Require authentication
from rest_framework import status, generics

from payments.models import TransactionDetails
from user.serializers import UserProfileSerializer
from .models import Listing, Amenities, Highlight, Interested  # Import all models
from .serializers import ListingSerializer, ListingCreateSerializer, \
    GetAllListDataSerializer, GetAllListUserNotLoginSerializer, ListingNearbySerializer, \
    InterestedSerializer, MyInterestsSerializer  # Import your ListingSerializer
from user.models import User

from .utils import check_image_for_text, calculate_distance
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.core.mail import EmailMessage
from datetime import datetime
from fpdf import FPDF


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
        if not listing.is_available:
            return Response({"message": "Listing Does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        # user_id = request.user.id if request.user.is_authenticated else None
        serializer = ListingSerializer(listing)
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        try:
            listing = Listing.objects.get(Q(user=user.id) & Q(is_available=True))
            print(listing)
            listing.is_available = False
            listing.save()

            user.is_host = False
            user.save()

            return Response({"message": "Listing Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Listing.DoesNotExist:
            return Response({"message": "Listing Does not exists"}, status=status.HTTP_404_NOT_FOUND)


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
            images = request.data.getlist('images')
            image_urls = []

            for image in images:
                if hasattr(image, 'chunks'):  # Check if image is an object with 'chunks' attribute
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
                        return Response({"message": "You cannot upload an image with Address or Number"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    else:
                        # Upload image to Cloudinary
                        upload_data = cloudinary.uploader.upload(image_path)
                        url = upload_data['url']
                        image_urls.append(url)
                        # Remove local image file after uploading
                        os.remove(image_path)
                else:
                    # Image is already a URL, directly append it
                    image_urls.append(image)

            print("image_urls", image_urls)
            setattr(listing, "image_urls", image_urls)

            for key, value in request.data.items():
                if key == 'images':
                    pass
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
            return Response({'error': 'You are not authorized to update this listing'},
                            status=status.HTTP_403_FORBIDDEN)


class NearbyPostsAPIView(APIView):
    def get(self, request, listId):
        # Get the current post object
        current_post = get_object_or_404(Listing, pk=listId)

        # Fetch user's ID
        user_id = request.user.id

        current_post_data = {
            'id': current_post.id,
            'latitude': current_post.latitude,
            'longitude': current_post.longitude
        }

        # Fetch nearby posts based on the current post's location
        nearby_posts = Listing.objects.exclude(pk=listId)

        # Exclude listings owned by the user
        # nearby_posts = nearby_posts.exclude(Q(user=user_id))

        # Serialize the nearby posts
        serializer = ListingNearbySerializer(nearby_posts, many=True)

        response_data = {
            'current_post': current_post_data,
            'nearby_posts': serializer.data
        }

        return Response(response_data)


class UserListProfileView(APIView):
    def get(self, request, listId):
        try:
            # Retrieve the listing based on the provided ListId
            listing = Listing.objects.get(id=listId)

            # Retrieve the user associated with the listing
            user = listing.user

            # Serialize the user data
            serializer = UserProfileSerializer(user)

            interested_status = Interested.objects.filter(listing=listId, user=request.user.id).exists()

            # Add interested status to the serialized data
            serialized_data = serializer.data
            serialized_data['interested'] = interested_status

            # Return the serialized user profile
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Listing.DoesNotExist:
            return Response({"message": "Listing does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InterestedCreateView(APIView):
    def post(self, request, listing_id, format=None):
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_host:
            return Response({'error': 'Hosts cannot express interest in listings'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = InterestedSerializer(data={'listing': listing_id, 'user': request.user.id})
            if serializer.is_valid():
                serializer.save(listing=listing, user=request.user)
                return Response({"message": "Successfully Interested"},
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'error': 'You have already expressed interest in this listing'},
                            status=status.HTTP_400_BAD_REQUEST)


class InterestedListView(APIView):
    def get(self, request, format=None):
        # Retrieve all interested listings for the current user
        interested_listings = Interested.objects.filter(user=request.user)

        # Sort the interested users by created_at field in descending order (latest first)
        interested_listings = interested_listings.order_by('-make_deal', '-created_at')

        # Serialize the interested listings
        serializer = MyInterestsSerializer(interested_listings, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)


class InterestedUsersListView(APIView):
    def get(self, request, format=None):
        try:
            # Retrieve the user's listing where is_available is True
            user_listing = Listing.objects.get(Q(user=request.user.id) & Q(is_available=True))
            listing_id = user_listing.id

            # Query the Interested objects based on the listing ID, excluding the logged-in user
            interested_users = Interested.objects.filter(listing=listing_id).exclude(user=request.user)

            # Sort the interested users by created_at field in descending order (latest first)
            interested_users = interested_users.order_by('-created_at')

            # Serialize the interested users
            serializer = InterestedSerializer(interested_users, many=True, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Listing.DoesNotExist:
            return Response({'error': 'User listing not found'}, status=status.HTTP_404_NOT_FOUND)
        except Interested.DoesNotExist:
            return Response({'error': 'No interested users found for this listing'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InterestedUserProfileView(APIView):
    def get(self, request, userId):
        try:
            # Retrieve the listing based on the provided ListId
            user = User.objects.get(id=userId)

            # Serialize the user data
            serializer = UserProfileSerializer(user)

            # Return the serialized user profile
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Listing.DoesNotExist:
            return Response({"message": "Listing does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# making a deal api views
class MakeDealAPIView(APIView):
    def post(self, request, format=None):
        listing_id = request.data.get('listingId')
        user_id = request.data.get('userId')

        try:
            interested = Interested.objects.get(listing_id=int(listing_id), user=int(user_id))
        except Interested.DoesNotExist:
            return Response({'error': 'User is not interested in this listing'}, status=status.HTTP_404_NOT_FOUND)

        if interested.make_deal:
            return Response({'error': 'Deal has already been initiated for this listing'},
                            status=status.HTTP_400_BAD_REQUEST)

        interested.make_deal = True
        interested.save()

        return Response({'success': 'Deal initiated successfully'}, status=status.HTTP_200_OK)


class ConfirmDealAPIView(APIView):
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Roommate Agreement Form", 0, 1, "C")

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, "C")

    def send_email_to_user(self, email, pdf_content):
        try:
            subject = 'Roommate Agreement Form'
            message = 'Please find attached the Roommate Agreement Form.'
            email_from = 'yashdodiya501@gmail.com'  # Replace with your email address
            recipient_list = [email]

            # Create an EmailMessage object
            email_message = EmailMessage(subject, message, email_from, recipient_list)
            email_message.attach('roommate_agreement.pdf', pdf_content, 'application/pdf')

            # Send email
            email_message.send()
        except Exception as e:
            raise e

    def generate_pdf(self, room_poster_name, room_seeker_name, rent_amount, room_address):
        pdf = self.PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Arial", "B", 12)

        pdf.cell(0, 10, f"Room Details: Address of the Room: {room_address}", ln=True)
        pdf.cell(0, 10, f"Terms of Occupancy: Monthly Rent: {rent_amount} to be paid by {room_seeker_name}", ln=True)

        pdf.set_font("Arial", "B", 12)

        pdf.cell(0, 10, "Responsibilities of Room Seeker:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10,
                       "- Paying rent and utilities on time.\n- Maintaining cleanliness and tidiness in shared areas.\n- Respecting the privacy and property of other occupants.\n- Informing Room Poster in advance about any guests or visitors.",
                       0, "L")

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Responsibilities of Room Poster:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10,
                       "- Providing a habitable living environment.\n- Handling repairs and maintenance promptly.\n- Respecting the privacy and property of Room Seeker.\n- Giving reasonable notice for any changes in the living arrangement.",
                       0, "L")

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10,
                 f"Termination of Agreement: Either party may terminate this Agreement with [Number of Days] days' notice in writing.",
                 ln=True)
        pdf.cell(0, 10, "Upon termination, Room Seeker shall vacate the premises and return keys to Room Poster.",
                 ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Authorization:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10,
                       "Both parties acknowledge that they have read and understood the terms of this Agreement.\nRoom Seeker agrees to abide by the rules and regulations set forth herein.\nRoom Poster agrees to provide a safe and comfortable living environment.",
                       0, "L")

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Signatures:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Room Seeker: {room_seeker_name} Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(0, 10, f"Room Poster: {room_poster_name} Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)

        return pdf.output(dest="S").encode("latin1")

    def post(self, request, listing_id, format=None):
        try:
            # Get the listing
            listing = Listing.objects.get(id=listing_id)

            user_transaction = TransactionDetails.objects.filter(
                Q(user=request.user.id) & Q(active_deposit=True)).first()

            if user_transaction is None:
                return Response({'error': 'You have to pay Deposit Amount'}, status=status.HTTP_404_NOT_FOUND)

            if listing.max_vacancy < 1:
                return Response({"error": "Vacancy is already full"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the interested user
            interest = Interested.objects.get(listing=listing.id, user=request.user, make_deal=True)

            # Check if the interested user has already confirmed a deal
            if interest.confirm_deal:
                return Response({'error': 'User has already confirmed a deal.'}, status=400)

            # Get the listing owner (user who created the listing)
            listing_owner = listing.user

            # Generate PDF content
            pdf_content = self.generate_pdf(listing_owner.name, request.user.name, listing.approx_rent,
                                            listing.location)

            # Send email to listing owner
            self.send_email_to_user(listing_owner.email, pdf_content)

            # Send email to interested user
            self.send_email_to_user(request.user.email, pdf_content)

            interest.confirm_deal = True
            user = User.objects.get(pk=request.user.id)
            user.confirmed_deal = True
            listing.max_vacancy -= 1

            listing.save()
            interest.save()
            user.save()

            return Response({'message': 'Deal confirmed and PDF sent successfully.'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class MyDealView(APIView):
    def get(self, request):
        try:
            # Get the logged in user's profile
            logged_in_user_profile = UserProfileSerializer(request.user).data

            # Find the listing where the current user confirmed the deal
            interested_listing = Interested.objects.filter(user=request.user, confirm_deal=True).first()

            if interested_listing:
                # Get the user who created the listing
                listing_owner_profile = UserProfileSerializer(interested_listing.listing.user).data
            else:
                listing_owner_profile = None

            return Response({
                'logged_in_user_profile': logged_in_user_profile,
                'listing_owner_profile': listing_owner_profile
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)
