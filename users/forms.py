import re
from django import forms
from django.contrib.auth.forms import PasswordChangeForm,PasswordResetForm,SetPasswordForm
from app_common.models import ContactMessage
from users.models import Batch,User, Payment, User, Course
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Sum
from django import forms
from django.forms.widgets import HiddenInput

class SignUpForm(forms.Form):

    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Full Name'}))
    username = forms.CharField(widget=forms.TextInput( attrs={'class': 'form-control','placeholder':'Enter Your Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Confirm Password'}))


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6 :
            raise ValidationError('Password length must be 6 characters.')

        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must contain at least one alphabet.')

        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number.')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter a Valid Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}))
    
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Valid Email Address','oninput': 'this.value = this.value.toLowerCase()'}))
    
 
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

class UpdateProfileForm(forms.Form):
    
    email = forms.EmailField(max_length=255)
    email.widget.attrs.update({'class': 'form-control','type':'text','placeholder':'Enter Email',"required":"required"})

    full_name = forms.CharField(max_length=255)
    full_name.widget.attrs.update({'class': 'form-control','type':'text','placeholder':'Enter Full Name',"required":"required"})

    contact = forms.CharField(max_length=10,help_text='Required. Enter Mobile Number',
    validators=[RegexValidator(regex=r'^[9876]\d{9}$')],widget=forms.TextInput(attrs={'class': 'form-control'}))

    profile_pic = forms.FileField(label='Select an image file', required=False)
    profile_pic.widget.attrs.update({'class': 'form-control', 'type': 'file'})


class AddressForm(forms.Form):
    Address1 = forms.CharField(max_length=255)
    Address1.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    Address2 = forms.CharField(max_length=255)
    Address2.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    contact = forms.CharField(max_length=10,help_text='Required. Enter Mobile Number',
    validators=[RegexValidator(regex=r'^[9876]\d{9}$')],
    widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    country = forms.CharField(max_length=255)
    country.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    state = forms.CharField(max_length=255)
    state.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    city = forms.CharField(max_length=255)
    city.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})
    
    pincode = forms.IntegerField()
    pincode.widget.attrs.update({'class': 'form-control','type':'text','placeholder':'Enter Pincode',"required":"required"})


class EditUserForm(forms.Form):
    model =User
    email = forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control"}))
    full_name = forms.CharField(label="Full Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    contact = forms.IntegerField(label="Contact",widget=forms.NumberInput(attrs={"class":"form-control"}))


class AddUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'contact', 'password']  # Include necessary fields

    password = forms.CharField(widget=forms.PasswordInput)

class StudentForm(forms.ModelForm):
    registered_user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_admitted=False, is_superuser=False),
        required=False,
        empty_label="Select a Registered User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    total_fees = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    balance = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    course_fees = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = User
        fields = [
            'registered_user',
            'student_image', 'student_signature', 'roll_number', 'abbreviation', 'full_name', 'select_one',
            'father_husband_name', 'mother_name', 'course_of_interest',
            'email', 'contact', 'alternative_contact', 'date_of_birth', 'gender', 'state', 'city', 'pincode',
            'permanent_address', 'aadhar_card_number', 'caste', 'qualification', 'occupation', 'course_fees',
            'discount_rate', 'discount_amount', 'fees_received', 'remarks', 'batch', 'remaining_seats_for_batch',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
            'display_admission_form_id_card_fees_recipt': forms.RadioSelect(choices=User.YESNO),
            'remaining_seats_for_batch':forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }
        labels = {
            'father_husband_name': 'Father/Husband Name',
        }

    def __init__(self, *args, **kwargs):
        # Fetch and remove 'course_id' and 'admit_existing_user' if provided
        course_id = kwargs.pop('course_id', None)
        self.admit_existing_user = kwargs.pop('admit_existing_user', False)
        super().__init__(*args, **kwargs)

        # Customize the display of registered users in the dropdown
        self.fields['registered_user'].label_from_instance = self.get_user_label

        # Populate course fees based on course_of_interest
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                self.fields['course_fees'].initial = course.course_fees
            except Course.DoesNotExist:
                self.fields['course_fees'].initial = "Course not found"

    def get_user_label(self, obj):
        """Customize the label to show full name with username."""
        return f"{obj.full_name} ({obj.username})"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validate email only if not admitting an existing user
        if not self.admit_existing_user and User.objects.filter(email=email, is_admitted=True).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        # Validate contact only if not admitting an existing user
        if not self.admit_existing_user and User.objects.filter(contact=contact, is_admitted=True).exists():
            raise ValidationError("A user with this contact number already exists.")
        return contact

    def clean_aadhar_card_number(self):
        aadhar = self.cleaned_data.get('aadhar_card_number')
        if not re.match(r"^\d{12}$", aadhar):  # Exactly 12 digits
            raise ValidationError("Please enter a valid 12-digit Aadhaar number.")
        return aadhar

class StudentPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'course', 'amount', 'payment_mode', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'value': '0.00', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    balance = forms.DecimalField(
        label='Total Balance', 
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    payment_mode = forms.ChoiceField(
        choices=Payment.PAYMENT_MODE_CHOICES,
        label='Payment Mode',
    )

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id', None)
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)
        
        # Filter student and course fields
        self.fields['student'].queryset = User.objects.filter(is_superuser=False)
        self.fields['course'].queryset = Course.objects.all()
        
        # Dynamically set the balance if student and course IDs are provided
        if student_id and course_id:
            self.fields['balance'].initial = self.calculate_balance(student_id, course_id)

    def calculate_balance(self, student_id, course_id):
        student = User.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        total_payments = student.payments.aggregate(Sum('amount'))['amount__sum'] or 0
        balance = course.course_fees - total_payments
        return balance

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'timing','total_seats']

class ContactMessageForm(forms.ModelForm):
    file = forms.FileField(required=False)
    class Meta:
        model = ContactMessage
        fields = ['message', 'contact', 'email']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Please add your queries here...', 'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),

        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'student_image', 'date_of_birth', 'contact', 'email', 'permanent_address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
