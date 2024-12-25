from datetime import datetime, timedelta
from decimal import Decimal
import random
import string
import bleach
from django.db import models
from django.contrib.auth.models import AbstractBaseUser ,PermissionsMixin
from django.urls import reverse
# from course.models import Course
from users.manager import MyAccountManager
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from helpers import utils
from django.conf import settings
from helpers.methods import request_deletion, cancel_deletion
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
import uuid


STATE_CHOICES = [
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
]
def generate_unique_username():
    while True:
        # Generate a random string of 8 characters (letters and digits)
        username = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Check if the username already exists
        if not User.objects.filter(username=username).exists():
            return username
        
class Batch(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    timing = models.CharField(max_length=50, blank=True, null=True)
    number_of_students = models.PositiveIntegerField(blank=True, null=True) 
    total_seats = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.upper()
        super().save(*args, **kwargs)

    def get_remaining_seats(self):
        return self.total_seats - (self.number_of_students or 0)

    def __str__(self):
        return self.name or "Unknown Batch"
    
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
    
    def save(self, *args, **kwargs):  
        # Clean HTML from eligibility and course_syllabus fields  
        self.eligibility = bleach.clean(self.eligibility,strip=False)  
        self.course_syllabus = bleach.clean(self.course_syllabus,strip=False)  
        super().save(*args, **kwargs) 

    def __str__(self):
        return self.course_name 

class User(AbstractBaseUser, PermissionsMixin):
    YESNO = (
        ("yes", "yes"),
        ("no", "no"),
    )
    DISCOUNT_CHOICES = [
        ('amount-', 'Amount -'),
        ('percent-', 'Percent -'),
    ]
    student_image = models.ImageField(upload_to='student_photos/', max_length=250, blank=True, null=True)
    student_signature = models.ImageField(upload_to='student_signatures/', max_length=250, blank=True, null=True)
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    abbreviation = models.CharField(max_length=10, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.')], blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    select_one = models.CharField(max_length=10, choices=[('S/O', 'S/O'), ('D/O', 'D/O'), ('W/O', 'W/O')], blank=True)
    father_husband_name = models.CharField(max_length=100, blank=True)
    show_father_husband_on_certificate = models.BooleanField(default=False)
    mother_name = models.CharField(max_length=100, blank=True)
    course_of_interest = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    username = models.CharField(max_length=10, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    contact = models.CharField(max_length=10, null=True, blank=True, unique=True)
    alternative_contact = models.CharField(max_length=10, null=True, blank=True, unique=True)
    date_of_birth = models.DateField(default=timezone.now)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    permanent_address = models.TextField(blank=True)
    aadhar_card_number = models.CharField(max_length=12, blank=True)
    caste = models.CharField(
    max_length=50,
    choices=[
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC/ST', 'SC/ST'),
        ('Others', 'Others'),
    ],
)
    qualification = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    batch = models.ForeignKey('Batch', on_delete=models.SET_NULL, null=True, blank=True)
    remaining_seats_for_batch = models.PositiveIntegerField(blank=True, null=True)
    display_admission_form_id_card_fees_recipt = models.CharField(max_length=10, choices=YESNO, default="yes")
    course_fees = models.FloatField(max_length=100, blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    discount_rate = models.CharField(max_length=10, choices=DISCOUNT_CHOICES, default='amount-', blank=True)
    discount_amount = models.FloatField(null=True, blank=True)
    total_fees = models.FloatField(default=0.0, null=True, blank=True, editable=False)
    fees_received = models.FloatField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    remarks = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admitted = models.BooleanField(default=False)

    deletion_requested = models.BooleanField(default=False)
    deletion_date = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["password"]

    objects = MyAccountManager()

    def save(self, *args, **kwargs):
        if self.course_of_interest:
            self.course_fees = self.course_of_interest.course_fees or 0.0
            self.total_fees = self.course_fees - Decimal(self.discount_amount or 0)
            self.balance = self.total_fees - Decimal(self.fees_received or 0)
        else:
            self.course_fees = 0.0
            self.total_fees = 0.0
            self.balance = 0.0
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name if self.full_name else "Unnamed User"
    
    @property
    def user_type_display(self):
        return "Student" if self.is_admitted else "User"
    def generate_reset_password_token(self):
        self.token = str(uuid.uuid4())
        self.token_expiration = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour
        self.save()
        return self.token

    def reset_password(self, token, new_password):
        if self.token == token and datetime.now() <= self.token_expiration:
            self.set_password(new_password)
            self.token = None  # Clear the token
            self.token_expiration = None  # Clear expiration
            self.save()
            return True
        return False
    
class Payment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('demand draft', 'Demand Draft'),
        ('online transfer', 'Online Transfer'),
        ('account adjustment', 'Account Adjustment')
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField(default=0.0, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
    

class OnlineClass(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    expiry_date = models.DateField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title

class Support(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid mobile number.')]
    )
    email = models.EmailField(blank=True, null=True)
    file = models.FileField(upload_to='support_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Support Request by {self.user.username} - {self.created_at}"
    

class Exam(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('appeared', 'Appeared'),
        ('postponed', 'Postponed'),
        ('cancel', 'Cancel'),
     )
    exam_name = models.CharField(max_length=200, default='exam', blank=True)
    date = models.DateField(default=timezone.now)  # This will now work correctly
    duration = models.DurationField(help_text="Enter the duration in HH:MM:SS format")
    total_marks = models.PositiveIntegerField(null=False, blank=False)
    total_questions = models.PositiveIntegerField(null=True, blank=True, help_text="Enter the total number of questions")
    passing_marks = models.PositiveIntegerField(null=True, blank=True, help_text="Enter the minimum passing marks")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    subjects = models.JSONField(default=list, blank=True)
    batch = models.ForeignKey('users.Batch', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
  
    def __str__(self):
        return self.get_status_display()

    class Meta:
        verbose_name = 'Exam Status'
        verbose_name_plural = 'Exam Statuses'
def __str__(self):
        return f"{self.course} - {self.exam_date}"

class ExamResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_results', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exam_results', null=True, blank=True)
    obtained_theory_marks = models.IntegerField(null=True, blank=True, default=0)
    obtained_practical_marks = models.IntegerField(null=True, blank=True, default=0)
    total_mark = models.FloatField(default=0)
    obtained_mark = models.FloatField(null=True, blank=True, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=2, choices=[
        ('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C')
    ], blank=True)
    result = models.CharField(max_length=7, choices=[('passed', 'Passed'), ('failed', 'Failed')], blank=True)
    created_on = models.DateField(auto_now_add=True)
    subjects_data = models.JSONField(default=list)

    def __str__(self):
        student_name = self.student.full_name if self.student else "Unknown Student"
        course_name = self.course.course_name if self.course else "No Course"
        return f"Result for {student_name} in {course_name}"

    def save(self, *args, **kwargs):
        # Calculate obtained marks
        self.obtained_mark = (self.obtained_theory_marks or 0) + (self.obtained_practical_marks or 0)

        # Calculate percentage if total_mark is valid
        if self.total_mark > 0:
            self.percentage = (self.obtained_mark / self.total_mark) * 100

        # Determine grade based on percentage
        if self.percentage >= 85:
            self.grade = 'A+'
        elif self.percentage >= 70:
            self.grade = 'A'
        elif self.percentage >= 55:
            self.grade = 'B'
        elif self.percentage >= 40:
            self.grade = 'C'
        else:
            self.grade = None  # No grade below 40%

        # Set result status
        self.result = 'passed' if self.grade in ['A+', 'A', 'B', 'C'] else 'failed'

        super().save(*args, **kwargs)

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