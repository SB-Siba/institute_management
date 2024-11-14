import re
from django import forms
from django.contrib.auth.forms import PasswordChangeForm,PasswordResetForm,SetPasswordForm
from users.models import Batch, ReAdmission, Support, User, Installment, Payment, User, Course
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Sum
from django import forms
from django.forms.widgets import HiddenInput

class SignUpForm(forms.Form):

    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Full Name'}))
    email = forms.EmailField(max_length=254,
    widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Enter Valid Email Address'}))
    contact = forms.CharField(max_length=10,
    validators=[RegexValidator(regex='^[9876]\d{9}$')],widget=forms.TextInput(attrs={'class': 'form-control','Placeholder':'Enter Mobile Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Confirm Password'}))



    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address already exists")
        return email

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if User.objects.filter(contact=contact).exists():
            raise forms.ValidationError("Contact number already exists")
        return contact


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
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Valid Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}))
    
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user found with this email address.")
        return email
 
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
 


class UpdateProfileForm(forms.Form):
    
    email = forms.EmailField(max_length=255)
    email.widget.attrs.update({'class': 'form-control','type':'text','placeholder':'Enter Email',"required":"required"})

    full_name = forms.CharField(max_length=255)
    full_name.widget.attrs.update({'class': 'form-control','type':'text','placeholder':'Enter Full Name',"required":"required"})

    contact = forms.CharField(max_length=10,help_text='Required. Enter Mobile Number',
    validators=[RegexValidator(regex='^[9876]\d{9}$')],widget=forms.TextInput(attrs={'class': 'form-control'}))

    profile_pic = forms.FileField(label='Select an image file', required=False)
    profile_pic.widget.attrs.update({'class': 'form-control', 'type': 'file'})



class AddressForm(forms.Form):
    Address1 = forms.CharField(max_length=255)
    Address1.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    Address2 = forms.CharField(max_length=255)
    Address2.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    contact = forms.CharField(max_length=10,help_text='Required. Enter Mobile Number',
    validators=[RegexValidator(regex='^[9876]\d{9}$')],widget=forms.TextInput(attrs={'class': 'form-control'}))
    
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
    total_fees = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    balance = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    course_fees = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
   
    class Meta:
        model = User
        fields = [
            'student_image', 'student_signature', 'roll_number', 'abbreviation', 'full_name', 'select_one',
            'father_husband_name', 'show_father_husband_on_certificate', 'mother_name', 'course_of_interest',
            'email', 'contact', 'alternative_contact', 'date_of_birth', 'gender', 'state', 'city', 'pincode',
            'permanent_address', 'aadhar_card_number', 'caste', 'qualification', 'occupation', 'course_fees',
            'discount_rate', 'discount_amount', 'fees_received', 'remarks', 'batch', 'remaining_seats_for_batch',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
            'display_admission_form_id_card_fees_recipt': forms.RadioSelect(choices=User.YESNO),
        }
        labels = {
            'father_husband_name': 'Father/Husband name',
            'show_father_husband_on_certificate': 'Show father/husband on certificate'
        }
 
    def __init__(self, *args, **kwargs):
        # Fetch and remove the 'course_id' and 'admit_existing_user' if provided
        course_id = kwargs.pop('course_id', None)
        self.admit_existing_user = kwargs.pop('admit_existing_user', False)
       
        super().__init__(*args, **kwargs)
       
        # Populate course fees based on course_of_interest
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                self.fields['course_fees'].initial = course.course_fees
            except Course.DoesNotExist:
                self.fields['course_fees'].initial = "Course not found"
   
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

class ReAdmissionForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(course_of_interest__isnull=False), required=True, label="Select Student")
    course_of_interest = forms.ModelChoiceField(queryset=Course.objects.filter(status='Active'), required=True, label="Course of Interest")
    exam_type = forms.ChoiceField(choices=[('OFFLINE', 'OFFLINE'), ('ONLINE', 'ONLINE')], required=True, label="Select Exam Type")
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=True)
    course_fees = forms.DecimalField(required=False, widget=forms.HiddenInput())
    discount_rate = forms.CharField(required=False, widget=forms.HiddenInput())
    discount_amount = forms.DecimalField(required=False, widget=forms.HiddenInput())
    total_fees = forms.DecimalField(required=False, widget=forms.HiddenInput())
    fees_received = forms.DecimalField(required=False, widget=forms.HiddenInput())
    balance = forms.DecimalField(required=False, widget=forms.HiddenInput())


    class Meta:
        model = ReAdmission  
        fields = ['student', 'course_of_interest', 'exam_type', 'batch', 
                  'course_fees', 'discount_rate', 'discount_amount', 
                  'total_fees', 'fees_received', 'balance', 'date', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter any remarks here...'}),
        }
    def __init__(self, *args, **kwargs):
        super(ReAdmissionForm, self).__init__(*args, **kwargs)
    
        
        
class InstallmentForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ['installment_name', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount == '':
            return 0  # Default to 0 if no amount is entered
        if amount < 0:
            raise ValidationError("Amount cannot be negative.")
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError("Date is required.")
        return date

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
        fields = ['name', 'timing','number_of_students','total_seats']

class SupportForm(forms.ModelForm):
    file = forms.FileField(required=False, label="Attach Files")
    class Meta:
        model = Support
        fields = ['description', 'mobile', 'email', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Please add your queries here...', 'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),

        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'student_image', 'date_of_birth', 'contact', 'email', 'permanent_address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
