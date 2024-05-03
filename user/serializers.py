from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from . import models
from .models import UserPreference


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = models.User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs['password'],
        password2 = attrs['password2'],
        if password != password2:
            raise serializers.ValidationError("password and confirm password not match")
        return attrs

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200)

    class Meta:
        model = models.User
        fields = ['id', 'email', 'password']


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'email', 'name', 'gender', 'phone_no', 'occupation', 'is_host', 'is_verified', 'age', 'bio',
                  'profile_image', 'confirmed_deal']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['name', 'phone_no', 'profile_image', 'email', 'gender', 'occupation', 'bio', 'age', 'is_host',
                  'is_verified', 'confirmed_deal', 'is_paid']


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = (
            'night_owl', 'party_lover', 'early_bird',
            'pet_lover', 'studious', 'vegan', 'fitness_freak',
            'non_alcoholic', 'sporty', 'music_lover', 'non_smoker', 'wanderer'
        )

    def create(self, validated_data):
        user = self.context['request'].user  # Get the user from the request
        validated_data['user'] = user  # Assign the user to the validated data
        return super().create(validated_data)

    def get_user_name(self, obj):
        return obj.user.name if obj.user else None
