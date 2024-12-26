from django.conf import settings
from django.db import models
from course.models import Course, ExamResult
from users.models import Batch, User
from django.utils import timezone



class ApprovedCertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, blank=True, null=True)  
    applied_date = models.DateField(default=timezone.now,null=True, blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    certificate_no = models.CharField(max_length=15, unique=True, blank=True, null=True)
    exam_result = models.OneToOneField(ExamResult, on_delete=models.SET_NULL, related_name='approved_certificate', null=True, blank=True, help_text="Link to the related exam result")

    def __str__(self):
        return f"Approved Certificate for {self.user} - {self.course}"


class CertificateDesign(models.Model):
    pass


class Requested(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, blank=True, null=True)  
    applied_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, blank=True, null=True)
    exam_data = models.JSONField(default=dict, blank=True, null=True) 

    def __str__(self):
        return f"Requested Certificate for {self.user} - {self.course}"