from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from user.models import User


# Create your models here.
class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    max_vacancy = models.IntegerField(validators=[MaxValueValidator(20)])
    description = models.TextField()
    PROPERTY_TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('room', 'Room'),
        # Add more choices as needed
    )
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    amenities = models.ManyToManyField('Amenities', blank=True)
    lease_term = models.IntegerField(validators=[MaxValueValidator(99)])
    PET_POLICY_CHOICES = (
        ('allowed', 'Allowed'),
        ('not_allowed', 'Not Allowed'),
    )
    pet_policy = models.CharField(max_length=50, choices=PET_POLICY_CHOICES)
    SMOKING_POLICY_CHOICES = (
        ('allowed', 'Allowed'),
        ('not_allowed', 'Not Allowed'),
    )
    smoking_policy = models.CharField(max_length=50, choices=SMOKING_POLICY_CHOICES)

    location = models.CharField()

    OCCUPANCY_CHOICES = (
        ('single', 'Single'),
        ('shared', 'Shared'),
        ('any', 'Any'),
    )
    occupancy = models.CharField(max_length=50, choices=OCCUPANCY_CHOICES)

    LOOKING_FOR_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('any', 'Any'),
    )
    looking_for = models.CharField(max_length=50, choices=LOOKING_FOR_CHOICES)

    approx_rent = models.IntegerField(validators=[MinValueValidator(0)])

    AMENITIES_CHOICES = (
        ('tv', 'TV'),  # Corrected typo (Tv -> TV)
        ('power_backup', 'Power Backup'),
        ('fridge', 'Fridge'),
        ('cook', 'Cook'),
        ('kitchen', 'Kitchen'),
        ('parking', 'Parking'),
        ('wifi', 'Wifi'),
        ('washing_machine', 'Washing Machine'),  # Changed name for clarity (Machine -> Washing Machine)
        ('ac', 'AC'),
    )
    amenities = models.ManyToManyField('Amenities', blank=True)  # Changed model name for consistency

    HIGHLIGHTS_CHOICES = (
        ('attached_washroom', 'Attached Washroom'),
        ('gated_society', 'Gated Society'),
        ('park_nearby', 'Park Nearby'),
        ('market_nearby', 'Market Nearby'),
        ('no_restriction', 'No Restriction'),
        ('attached_balcony', 'Attached Balcony'),
        ('close_to_metro_station', 'Close to Metro Station'),
        ('newly_built', 'Newly Built'),
        ('separate_washrooms', 'Separate Washrooms'),
        ('house_keeping', 'House Keeping'),
        ('public_transport_nearby', 'Public Transport Nearby'),
        ('gym_nearby', 'Gym Nearby'),
    )
    highlights = models.ManyToManyField('Highlight', blank=True)

    mobile_visible = models.BooleanField(default=True)  # Added mobile_visible field

    # array field of a image urls
    image_urls = ArrayField(models.URLField(), blank=True, default=list)

    def __str__(self):
        return f"{self.location} - {self.occupancy}"

    # def get_absolute_url(self):
    #     return reverse('listing_detail', kwargs={'pk': self.pk})  # Assuming a detail view

    # def __str__(self):
    #     return self.title


class Amenities(models.Model):
    name = models.CharField(max_length=255, choices=Listing.AMENITIES_CHOICES, unique=True)

    def __str__(self):
        return f"{self.name} - {self.id}"


class Highlight(models.Model):
    name = models.CharField(max_length=255, choices=Listing.HIGHLIGHTS_CHOICES, unique=True)

    def __str__(self):
        return f"{self.name} - {self.id}"
