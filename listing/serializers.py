from rest_framework import serializers

from user.models import UserPreference, User
from .models import Listing, Amenities, Highlight, Interested
from .utils import calculate_distance


class ListingSerializer(serializers.ModelSerializer):
    amenities = serializers.SerializerMethodField()
    highlights = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_occupation = serializers.CharField(source='user.occupation', read_only=True)
    user_gender = serializers.CharField(source='user.gender', read_only=True)
    user_profile_image = serializers.CharField(source='user.profile_image', read_only=True)
    match_details = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = '__all__'

    def get_amenities(self, instance):
        return [amenity.name for amenity in instance.amenities.all()]

    def get_highlights(self, instance):
        return [highlight.name for highlight in instance.highlights.all()]

    def get_match_details(self, instance):
        # Retrieve preferences of the user who created the listing
        listing_user_preferences = instance.user.preferences

        # Get names of user preferences with a value of True
        user_true_preferences = [field.name for field in UserPreference._meta.get_fields() if
                                 getattr(listing_user_preferences, field.name) and field.name not in ['id', 'user']]

        # Return match details along with matching percentage
        return {
            'user_preferences': user_true_preferences
        }


class GetAllListDataSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_occupation = serializers.CharField(source='user.occupation', read_only=True)
    user_profile_image = serializers.CharField(source='user.profile_image', read_only=True)
    match_details = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'location', 'user_name', 'user_occupation', 'user_profile_image', 'match_details',
                  'approx_rent', 'occupancy', 'looking_for', 'distance']

    def get_match_details(self, instance):
        # Retrieve preferences of the logged-in user
        logged_in_user_preferences = self.context['request'].user.preferences

        # Retrieve preferences of the user who created the listing
        listing_user_preferences = instance.user.preferences

        # Initialize dictionaries to store matched and unmatched fields
        matched_fields = []
        unmatched_fields = []

        # Calculate matching fields and percentages
        total_fields = 0
        matching_fields = 0
        logged_in_user_preferences_total = 0

        for field in UserPreference._meta.get_fields():

            if field.name != 'user' and field.name != 'id':
                logged_in_user_value = getattr(logged_in_user_preferences, field.name)

                if logged_in_user_value:
                    logged_in_user_preferences_total += 1

        # Iterate through fields of UserPreference model
        for field in UserPreference._meta.get_fields():
            # Exclude 'user' field from comparison
            if field.name != 'user' and field.name != 'id':
                total_fields += 1
                # Check if the field is True for both users
                logged_in_user_value = getattr(logged_in_user_preferences, field.name)
                listing_user_value = getattr(listing_user_preferences, field.name)
                if logged_in_user_value and listing_user_value:
                    matched_fields.append(field.name)
                    matching_fields += 1
                else:
                    unmatched_fields.append(field.name)

        # Calculate matching percentage
        match_percentage = (matching_fields / logged_in_user_preferences_total) * 100 if total_fields > 0 else 0

        # Get names of user preferences with a value of True
        user_true_preferences = [field.name for field in UserPreference._meta.get_fields() if
                                 getattr(listing_user_preferences, field.name) and field.name not in ['id', 'user']]

        # Return match details along with matching percentage
        return {
            'match_percentage': int(match_percentage),
            'matched_fields': matched_fields,
            'unmatched_fields': unmatched_fields,
            'user_preferences': user_true_preferences
        }

    def get_distance(self, instance):
        # Get user's location from the request context
        if self.context.get('user_latitude') is not None:
            user_latitude = float(self.context.get('user_latitude'))
            user_longitude = float(self.context.get('user_longitude'))

            if user_latitude is not None and user_longitude is not None:
                # Calculate distance using Haversine formula
                listing_latitude = instance.latitude
                listing_longitude = instance.longitude

                if listing_latitude is not None and listing_longitude is not None:
                    # Calculate distance using your distance calculation method
                    distance = calculate_distance(
                        user_latitude, user_longitude, listing_latitude, listing_longitude
                    )
                    return distance

        return None


class GetAllListUserNotLoginSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_occupation = serializers.CharField(source='user.occupation', read_only=True)
    user_profile_image = serializers.CharField(source='user.profile_image', read_only=True)
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'location', 'user_name', 'user_occupation', 'user_profile_image',
                  'approx_rent', 'occupancy', 'looking_for', 'distance']

    def get_distance(self, instance):
        # Get user's location from the request context
        user_latitude = self.context.get('user_latitude')
        user_longitude = self.context.get('user_longitude')

        if user_latitude is not None and user_longitude is not None:
            # Calculate distance using Haversine formula
            listing_latitude = instance.latitude
            listing_longitude = instance.longitude

            if listing_latitude is not None and listing_longitude is not None:
                # Calculate distance using your distance calculation method
                distance = calculate_distance(
                    user_latitude, user_longitude, listing_latitude, listing_longitude
                )
                return distance

        return None


class ListingCreateSerializer(serializers.ModelSerializer):
    amenities = serializers.PrimaryKeyRelatedField(queryset=Amenities.objects.all(), many=True)
    highlights = serializers.PrimaryKeyRelatedField(queryset=Highlight.objects.all(), many=True)

    class Meta:
        model = Listing
        fields = '__all__'


class ListingNearbySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    profile_image = serializers.URLField(source='user.profile_image', read_only=True)
    class Meta:
        model = Listing
        fields = ['id', 'latitude', 'longitude', 'user_name', 'profile_image']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'gender', 'phone_no', 'occupation', 'age', 'bio', 'profile_image']


class InterestedSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Interested
        fields = '__all__'


class MyInterestsSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='listing.user')
    class Meta:
        model = Interested
        fields = '__all__'
