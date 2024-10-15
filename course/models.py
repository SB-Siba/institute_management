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

    # DISCOUNT_CHOICES = [
    #     ('amount-', 'Amount -'),
    #     ('amount+', 'Amount +'),
    #     ('percent-', 'Percent -'),
    #     ('percent+', 'Percent +'),
    # ]

    course_code = models.CharField(max_length=100, unique=True)
    award = models.ForeignKey(AwardCategory,on_delete=models.CASCADE, null=True ,blank=True)
    course_name = models.CharField(max_length=200)
    course_subject = models.CharField(max_length=200,default='')
    course_fees = models.DecimalField(max_digits=10, decimal_places=2)
    course_mrp = models.DecimalField(default=0.0 ,max_digits=10, decimal_places=2)
    minimum_fees = models.DecimalField(max_digits=10, decimal_places=2)
    course_duration = models.CharField(max_length=100)
    exam_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_video_link_1 = models.URLField(blank=True, null=True)
    course_video_link_2 = models.URLField(blank=True, null=True)
    course_syllabus = models.TextField()
    eligibility = models.TextField()
    course_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    pdf_files = models.FileField(upload_to='course_materials/', blank=True, null=True)
    course_video_links = models.JSONField(default=list, blank=True, null=True)
    display_course_fees_on_website = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')


    def __str__(self):
        return self.course_name
    
    def calculate_fees(self, fees_received=0):
        """
        Calculate the discount amount, total fees, and balance.
        """
        if self.discount_rate:
            discount_rate = float(self.discount_rate)
        else:
            discount_rate = 0

        if self.discount_rate == 'amount+':
            self.discount_amount = max(0, discount_rate)
        elif self.discount_rate == 'amount-':
            self.discount_amount = min(self.course_fees, discount_rate)
        elif self.discount_rate == 'percent+':
            self.discount_amount = (self.course_fees * discount_rate) / 100
        elif self.discount_rate == 'percent-':
            self.discount_amount = (self.course_fees * discount_rate) / 100

        self.total_fees = self.course_fees - self.discount_amount
        self.balance = self.total_fees - fees_received
        self.save()