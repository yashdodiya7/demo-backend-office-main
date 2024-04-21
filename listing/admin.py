from django.contrib import admin

from listing.models import Listing, Amenities, Highlight

# Register your models here.
admin.site.register(Listing)
admin.site.register(Amenities)
admin.site.register(Highlight)