from django.contrib.auth.models import User
from django.db import models

from users.utils import image_resize


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_img.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} profile'

    def save(self, *args, **kwargs):
        # Ensure image stays within UI-friendly dimensions before persist.
        image_resize(self.image, 280, 280)
        super().save(*args, **kwargs)
