from django.db import models
from users.models import User
from helpers import utils
class ContactMessage(models.Model):
    
    uid=models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete= models.CASCADE, null= True, blank= True)
    name = models.CharField(max_length=255, null=True, blank=True)  # Added name field
    email = models.EmailField(null=True, blank=True,unique=True)
    contact = models.CharField(max_length= 10, null=True, blank=True, unique=True)
    message = models.TextField(null= True, blank= True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = utils.get_rand_number(5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user if self.user else self.email}"