from django.conf import settings
from django.db import models
from course.models import Course
from users.models import Batch, User
from django.utils import timezone



class ApprovedCertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, blank=True, null=True)  # Ensure this line is correct
    approved_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Approved Certificate for {self.user} - {self.course}"


class CertificateDesign(models.Model):
    applied_certificate = models.OneToOneField(
        ApprovedCertificate,
        on_delete=models.CASCADE,
        related_name='design',  # Explicitly defined reverse accessor
    )
    design_file = models.FileField(upload_to='certificates/')  # For storing certificate files
    designed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.applied_certificate.user}"
    
class Requested(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    applied_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, blank=True, null=True)
    exam_data = models.JSONField(default=dict, blank=True, null=True) 

    def __str__(self):
        return f"Requested Certificate for {self.user} - {self.course}"