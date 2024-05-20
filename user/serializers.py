from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers

from . import models
from .models import UserPreference, Contact
from .utils import Utils


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


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class UserPasswordResetEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = models.User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if models.User.objects.filter(email=email).exists():
            user = models.User.objects.get(email=email)
            # using this so in url safe id is shown not the actual one
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = (
                    "http://localhost:3000/reset-password/"
                    + uid
                    + "/"
                    + token
                    + "/"
            )
            body = "This is your reset password link " + link
            data = {"subject": "Reset Password", "body": body, "to_email": user.email}

            # print("reset ", link)

            Utils.send_mail(data)
            return attrs
        else:
            raise serializers.ValidationError("Provided email is not valid user")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=200, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=200, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = models.User
        fields = ["password", "password2"]

    def validate(self, attrs):

        password = attrs.get("password")
        password2 = attrs.get("password2")
        uid = self.context.get("uid")
        token = self.context.get("token")

        # print("uid ", uid)
        # print("token ", token)

        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password are not same"
            )
        id = int(smart_str(urlsafe_base64_decode(uid)))
        # print("id ", type(id))
        user = models.User.objects.get(id=id)
        print("User ", user)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is either invalid or expired")
        user.set_password(password)
        user.save()
        return attrs
