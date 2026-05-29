from django.contrib import admin

from hotel.models import Booking, Profile, Room

admin.site.register(Room)
admin.site.register(Profile)
admin.site.register(Booking)
