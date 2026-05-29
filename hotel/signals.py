from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from hotel.models import Profile


@receiver(post_save, sender=User)
def sync_profile_role_from_user(sender, instance, **kwargs):
    profile = Profile.objects.filter(user=instance).first()
    if profile:
        profile.sync_role_from_user()
