from django.contrib import admin
from .models import Booking, Profile, Room

# Register your models here.
admin.site.register(Room)
admin.site.register(Profile)
admin.site.register(Booking)
