from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from django.db import models


# Validators
# def rating_validator(value):
#     if value > 5 or value < 1:
#         raise ValidationError("Review Between 0 to 5")
#     else:
#         return value


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, name, gender, age, phone_no, confirmed_deal=None, is_paid=None, is_host=None,
                    is_verified=None, occupation=None, bio=None,
                    profile_image=None,
                    password=None,
                    password2=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            gender=gender,
            phone_no=phone_no,
            age=age,
        )

        if bio is not None:
            user.bio = bio

        if occupation is not None:
            user.phone_no = occupation

        if profile_image is not None:
            user.bio = profile_image

        if is_host:
            user.is_host = True

        if is_verified:
            user.is_verified = True

        if confirmed_deal:
            user.confirmed_deal = True

        if is_paid:
            user.is_paid = True

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_no, gender, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            phone_no=phone_no,
            gender=gender
        )
        user.is_admin = True
        # # extra_fields.setdefault('is_active', True)
        # extra_fields.setdefault('is_admin', True)
        # # extra_fields.setdefault('is_superuser', True)
        # extra_fields.setdefault('role', 1)
        # print(user.is_admin)

        user.save(using=self._db)
        return user


GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email",
        max_length=255,
        unique=True,
    )

    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, blank=True)
    PHONE_REGEX = r"(^\+91?\d{10})|^\+?\d{12}$"
    phone_no = models.CharField(max_length=20,
                                validators=[RegexValidator(PHONE_REGEX, 'Enter a valid phone number.')])
    occupation = models.CharField(max_length=255, blank=True)

    is_host = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    confirmed_deal = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    age = models.DecimalField(max_digits=2, decimal_places=0)
    bio = models.TextField(max_length=255, blank=True)
    profile_image = models.URLField(blank=True,
                                    default="https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714408857/rijmvo0cqksausiv3ejj.jpg")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    crated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name', 'phone_no', 'gender']

    def __str__(self):
        return self.email + " " + str(self.id)

    def has_perm(self, perm, obj=None):
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    night_owl = models.BooleanField(default=False)
    party_lover = models.BooleanField(default=False)
    early_bird = models.BooleanField(default=False)
    pet_lover = models.BooleanField(default=False)
    studious = models.BooleanField(default=False)
    vegan = models.BooleanField(default=False)
    fitness_freak = models.BooleanField(default=False)
    non_alcoholic = models.BooleanField(default=False)
    sporty = models.BooleanField(default=False)
    music_lover = models.BooleanField(default=False)
    non_smoker = models.BooleanField(default=False)
    wanderer = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name


class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    PHONE_REGEX = r"(^\+91?\d{10})|^\+?\d{12}$"
    phone_no = models.CharField(max_length=20,
                                validators=[RegexValidator(PHONE_REGEX, 'Enter a valid phone number.')])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
