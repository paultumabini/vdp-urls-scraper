# Create a default profile when a user is created
# the User is the sender; the one sending the signal
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


# When the user is saved, the sender will send the signal and receive @receiver
# instance --> is gonna be the user
# But in order the process to work, import the signal inside a "ready" function at .apps.py
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
