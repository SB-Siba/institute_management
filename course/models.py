
from django.db import models
from django.utils import timezone  
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



class Exam(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('appear', 'Appear'),
     )
    exam_name = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)  # This will now work correctly
    duration = models.DurationField(help_text="Enter the duration in HH:MM:SS format")
    total_marks = models.PositiveIntegerField(null=False, blank=False)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    batch = models.ForeignKey('users.Batch', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
  
    def __str__(self):
        return self.get_status_display()

    class Meta:
        verbose_name = 'Exam Status'
        verbose_name_plural = 'Exam Statuses'
def __str__(self):
        return f"{self.course} - {self.exam_date}"
 

class Student(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='student_photos/')
    course_name = models.CharField(max_length=255)
    # other fields related to students

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    theory_mark = models.DecimalField(max_digits=5, decimal_places=2)
    practical_mark = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, choices=[
        ('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')
    ])
    result = models.CharField(max_length=7, choices=[('passed', 'Passed'), ('failed', 'Failed')])
    created_on = models.DateField(auto_now_add=True)
    # other fields related to exam results

