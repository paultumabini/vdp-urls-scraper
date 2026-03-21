from django.contrib.auth.models import User
from django.db import models
from PIL import Image

from users.utils import image_resize


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_img.png', upload_to='profile_pics')
    # Note: default image must available at media dir, i.e: MEDIA_URL = '/images/'

    def __str__(self):
        return f'{self.user.username} profile'

    # Overide the save method in the backend
    def save(self, *args, **kwargs):
        # run the save method from the parent class and save the image no matter how large the image size is
        image_resize(self.image, 280, 280)
        super().save(*args, **kwargs)

    # Other option:
    # img = Image.open(self.image.path)

    # if img.height > 300 or img.width > 300:
    #     output_size = (300, 300)
    #     img.thumbnail(output_size)
    #     img.save(self.image.path)


# ! NOTES:
# Profile Model for image needs the PILLOW package in the backend
# The save(self) is the method that get runs after our Model is saved. It's a method that already exists in the parent Class, but we're creating our own so we can add some functionalities
