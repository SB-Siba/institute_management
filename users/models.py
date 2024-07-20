from django.db import models
from django.contrib.auth.models import AbstractBaseUser ,PermissionsMixin
from PIL import Image
from users.manager import MyAccountManager
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from helpers import utils
import uuid


def generate_random_string():
    random_uuid = uuid.uuid4()
    random_string = random_uuid.hex
    return random_string

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length= 255, null= True, blank= True)
    email = models.EmailField(null=True,blank=True,unique=True)
    password = models.TextField(null=True,blank=True)
    contact = models.CharField(max_length= 10, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="user_profile_pic/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    address = models.JSONField(default= dict, null=True, blank=True)
    
    wallet = models.FloatField(default=0.0)
   
    token = models.CharField(max_length=100, null=True, blank=True)
 
    # we are storing some extra data in the meta data field
    meta_data = models.JSONField(default= dict)
   
    USERNAME_FIELD = "email"    
    REQUIRED_FIELDS = ["password"]
 
    objects = MyAccountManager()
 
   


    @property
    def full_contact_number(self):
        if self.contact_number:
            contact_number = '+91' + self.contact_number
        else:
            contact_number='no contact present'

        return contact_number
    
    def get_token(self, *args, **kwargs):
        token= generate_random_string()
        self.token= token
        super().save(*args, **kwargs)
        return token

    def __str__(self):
        return self.email

    def send_reset_password_email(self):
        token = self.generate_reset_password_token()
        reset_link = f"http://35.154.55.245/reset-password/{token}/"
        subject = 'Reset your password'
        message = f'Hi {self.full_name},\n\nTo reset your password, please click the link below:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.'
        send_mail(subject, message, 'info@swastikwealthcare.com', [self.email])
        
        
        
    def generate_reset_password_token(self):
        token = str(uuid.uuid4())
        self.token = token
        self.save()
        return token
    
    def reset_password(self, token, new_password):
        # Check if the token is valid (you may want to implement token validation logic here)
        if self.token == token:
            # Set the new password and save the user
            self.set_password(new_password)
            self.token = None  # Clear the token after password reset
            self.save()
            return True
        else:
            return False

