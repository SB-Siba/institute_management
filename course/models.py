from django.db import models
from ckeditor.fields import RichTextField


class AwardCategory(models.Model):
    category_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name
    

class Course(models.Model):
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    course_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    award = models.ForeignKey(AwardCategory, on_delete=models.CASCADE, null=True, blank=True)
    course_name = models.CharField(max_length=200, blank=True, null=True)
    course_subject = models.JSONField(default=list, blank=True, null=True)
    course_fees = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    course_mrp = models.DecimalField(default=0.0 ,max_digits=10, decimal_places=2,blank=True, null=True)
    minimum_fees = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    course_duration = models.CharField(max_length=100,blank=True, null=True)
    exam_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_video_link_1 = models.URLField(blank=True, null=True)
    course_video_link_2 = models.URLField(blank=True, null=True)
    course_syllabus = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    course_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    pdf_files = models.FileField(upload_to='course_materials/', blank=True, null=True)
    course_video_links = models.JSONField(default=list, blank=True, null=True)
    display_course_fees_on_website = models.BooleanField(default=False,blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active',blank=True, null=True)
    batch = models.ForeignKey('users.Batch', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.course_name
    
    