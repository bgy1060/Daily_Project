from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, default="")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True,
                                  null=False)
    last_name = models.CharField(max_length=255, blank=True,
                                 null=False)

    withdrawal_status = models.BooleanField(default=False)
    withdrawal_date = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"