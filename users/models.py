from django.db import models
from django.contrib.auth.models import AbstractBaseUser ,PermissionsMixin
from PIL import Image
from users.manager import MyAccountManager
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from helpers import utils
import uuid
from helpers.methods import request_deletion , cancel_deletion

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
    deletion_requested = models.BooleanField(default=False)
    deletion_date = models.DateTimeField(null=True, blank=True)
    wallet = models.FloatField(default=0.0)
   
    token = models.CharField(max_length=100, null=True, blank=True)
 
    # we are storing some extra data in the meta data field
    meta_data = models.JSONField(default= dict)
   
    USERNAME_FIELD = "email"    
    REQUIRED_FIELDS = ["password"]
 
    objects = MyAccountManager()
 
    @property
    def __str__(self):
        return self.email

User.request_deletion = request_deletion
User.cancel_deletion = cancel_deletion
    