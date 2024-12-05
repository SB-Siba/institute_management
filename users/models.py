from datetime import datetime, timedelta
from decimal import Decimal
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser ,PermissionsMixin
from django.urls import reverse
from course.models import Course
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

class User(AbstractBaseUser, PermissionsMixin):
    YESNO = (
        ("yes", "yes"),
        ("no", "no"),
    )
    DISCOUNT_CHOICES = [
        ('amount-', 'Amount -'),
        ('percent-', 'Percent -'),
    ]
    courses = models.ManyToManyField(Course, related_name='students', blank=True)
    student_image = models.ImageField(upload_to='student_photos/', max_length=250, blank=True, null=True)
    student_signature = models.ImageField(upload_to='student_signatures/', max_length=250, blank=True, null=True)
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    abbreviation = models.CharField(max_length=10, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.')], blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    select_one = models.CharField(max_length=10, choices=[('S/O', 'S/O'), ('D/O', 'D/O'), ('W/O', 'W/O')], blank=True)
    father_husband_name = models.CharField(max_length=100, blank=True)
    show_father_husband_on_certificate = models.BooleanField(default=False)
    mother_name = models.CharField(max_length=100, blank=True)
    course_of_interest = models.ForeignKey('course.Course', on_delete=models.CASCADE, null=True, blank=True)
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
    
    
class Installment(models.Model):
    student = models.ForeignKey(User, related_name='installments', on_delete=models.CASCADE)
    installment_name = models.CharField(max_length=100)
    amount = models.FloatField(default=0.0, null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.installment_name} - {self.amount}"
        
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
    
class ReferralSettings(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)

    def __str__(self):
        return f"Referral Amount: {self.amount}"

class OnlineClass(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    expiry_date = models.DateField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title
    
class Attendance(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
    
class ReAdmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    course_fees = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)
    fees_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.student.full_name} - {self.course.course_name} - {self.date}"

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