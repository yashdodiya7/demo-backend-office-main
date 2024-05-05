import os
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django

django.setup()

from faker import factory, Faker

fake = Faker()

from listing.models import Listing, Amenities, Highlight
from user.models import User, UserPreference

# Initialize Faker
fake = Faker()

profile_images = [
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714717402/profile_images/agsmomsuufd0alnnocsb.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714737700/dm83cxvqsy77fjgdmywn.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714737700/ifey8zm2sm5gtck3vkg0.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714737701/erbya8zeksouxbddulps.png",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714460233/khu9yk1vfejz1eppgorz.jpg",
]

listing_images = [
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714728862/lwbywn075pr5rvwqwdzj.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714728861/uccp08fniu2npovik7my.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714720069/pv1nncejo9mdowmytfwk.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714720068/c2bm3nqdiftcuej9qjs9.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714719778/zlmp9mxwxe0ja4tbhnn5.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714719777/nynita1cl8dwpq876fcs.jpg",
    "https://res.cloudinary.com/dxwxpfxgi/image/upload/v1714466358/ii0rjp06wwie1zko4uaj.jpg",
]


def get_random_image_url(image_urls):
    return random.choice(image_urls)


# Function to create fake data for listings
def create_fake_listings(num_listings):
    for _ in range(num_listings):
        # Create a user for the listing
        user = User.objects.create(
            email=fake.email(),
            name=fake.name(),
            gender=random.choice(['male', 'female']),
            phone_no=fake.phone_number(),
            age=random.randint(18, 60),
            is_host=True,
            is_verified=random.choice([True, False]),
            confirmed_deal=False,
            is_paid=random.choice([True, False]),
            occupation=fake.job(),
            bio=fake.text(),
            profile_image=get_random_image_url(profile_images),
        )

        # Create user preferences
        UserPreference.objects.create(
            user=user,
            night_owl=random.choice([True, False]),
            party_lover=random.choice([True, False]),
            early_bird=random.choice([True, False]),
            pet_lover=random.choice([True, False]),
            studious=random.choice([True, False]),
            vegan=random.choice([True, False]),
            fitness_freak=random.choice([True, False]),
            non_alcoholic=random.choice([True, False]),
            sporty=random.choice([True, False]),
            music_lover=random.choice([True, False]),
            non_smoker=random.choice([True, False]),
            wanderer=random.choice([True, False]),
        )

        # Create the listing
        listing = Listing.objects.create(
            user=user,
            is_available=True,
            max_vacancy=random.randint(1, 20),
            description=fake.text(),
            property_type=random.choice(['apartment', 'house', 'room']),
            latitude=fake.latitude(),
            longitude=fake.longitude(),
            lease_term=random.randint(1, 21),
            pet_policy=random.choice(['allowed', 'not_allowed']),
            smoking_policy=random.choice(['allowed', 'not_allowed']),
            location=fake.address(),
            occupancy=random.choice(['single', 'shared', 'any']),
            looking_for=random.choice(['male', 'female', 'any']),
            approx_rent=random.randint(100, 5000),
            mobile_visible=random.choice([True, False]),
        )

        # Add amenities to the listing
        amenities = Amenities.objects.all()
        for _ in range(random.randint(1, len(amenities))):
            listing.amenities.add(random.choice(amenities))

        # Add highlights to the listing
        highlights = Highlight.objects.all()
        for _ in range(random.randint(1, len(highlights))):
            listing.highlights.add(random.choice(highlights))

        # Create interested users for the listing
        # for _ in range(random.randint(0, 10)):
        #     interested_user = User.objects.create(
        #         email=fake.email(),
        #         name=fake.name(),
        #         gender=random.choice(['male', 'female']),
        #         phone_no=fake.phone_number(),
        #         age=random.randint(18, 60),
        #         is_host=random.choice([True, False]),
        #         is_verified=random.choice([True, False]),
        #         confirmed_deal=random.choice([True, False]),
        #         is_paid=random.choice([True, False]),
        #         occupation=fake.job(),
        #         bio=fake.text(),
        #         profile_image=fake.image_url(),
        #     )
        #     Interested.objects.create(
        #         listing=listing,
        #         user=interested_user,
        #         make_deal=random.choice([True, False]),
        #         confirm_deal=random.choice([True, False]),
        #         deposit_paid=random.choice([True, False]),
        #     )


# Function to create fake data for amenities and highlights
# def create_fake_choices():
#     for choice in Listing.AMENITIES_CHOICES:
#         Amenities.objects.create(name=choice[0])
#     for choice in Listing.HIGHLIGHTS_CHOICES:
#         Highlight.objects.create(name=choice[0])
#
#
# # Call the functions to create fake data
# create_fake_choices()
create_fake_listings(2)  # Adjust the number of listings as needed
