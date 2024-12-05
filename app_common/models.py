from django.db import models
from users.models import User
from helpers import utils

class ContactMessage(models.Model):
    uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=10, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reply = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = utils.get_rand_number(5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or self.email} - {self.created_at}"