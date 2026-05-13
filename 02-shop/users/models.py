from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model. Email is the primary identifier (allauth)."""

    email = models.EmailField(unique=True)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
