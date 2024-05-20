from django.contrib import admin

from .models import User, UserPreference, Contact


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id' ,'email', 'name', 'phone_no')


admin.site.register(User, UserAdmin)
admin.site.register(UserPreference)
admin.site.register(Contact)
