from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import random
from datetime import timedelta
from django.utils import timezone

class OTP(models.Model):
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() <= self.created_at + timedelta(minutes=3)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
