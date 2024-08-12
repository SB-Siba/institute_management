from django.db import models
from django.contrib.auth.models import AbstractBaseUser ,PermissionsMixin
from PIL import Image
from django.urls import reverse
from users.manager import MyAccountManager
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from helpers import utils
import uuid
from django.conf import settings
from helpers.methods import request_deletion , cancel_deletion


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    contact = models.CharField(max_length=10, null=True, blank=True, unique=True)
    profile_pic = models.ImageField(upload_to="user_profile_pic/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    address = models.JSONField(default=dict, null=True, blank=True)
    deletion_requested = models.BooleanField(default=False)
    deletion_date = models.DateTimeField(null=True, blank=True)
    wallet = models.FloatField(default=0.0)
   
    token = models.CharField(max_length=100, null=True, blank=True)
 
    meta_data = models.JSONField(default=dict)
   
    # Define the field to be used as the username for authentication
    USERNAME_FIELD = "email"
    
    # Define the required fields for creating a user via the command line
    REQUIRED_FIELDS = ["full_name", "contact"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def send_reset_password_email(self):
        token = self.generate_reset_password_token()
        reset_link = f"{settings.SITE_URL}/reset-password/{token}/"
        subject = 'Reset your password'
        message = (
            f'Hi {self.full_name},\n\n'
            f'To reset your password, please click the link below:\n\n'
            f'{reset_link}\n\n'
            'If you did not request this, please ignore this email.'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    def generate_reset_password_token(self):
        token = str(uuid.uuid4())
        self.token = token
        self.save()
        return token

    def reset_password(self, token, new_password):
        if self.token == token:
            self.set_password(new_password)
            self.token = None  # Clear the token after password reset
            self.save()
            return True
        return False

# Assuming you have request_deletion and cancel_deletion functions defined somewhere
User.request_deletion = request_deletion
User.cancel_deletion = cancel_deletion