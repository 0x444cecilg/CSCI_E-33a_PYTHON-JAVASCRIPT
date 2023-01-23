from django.contrib.auth.models import AbstractUser
from django.db import models

from project4 import settings
from django.utils import timezone


class User(AbstractUser):
    pass


class Posting(models.Model):
    poster = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, blank=True, related_name="likes")

    def __str__(self):
        return f"Post {self.id}"

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": [user.username for user in self.likes.all()]
        }
    
    def count_likes(self):
        return self.likes.count()


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")
    followee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followees")

    def __str__(self):
        return f"{self.follower} follows {self.followee}"