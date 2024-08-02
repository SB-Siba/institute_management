from django import forms
from . import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class ContactMessageForm(forms.Form):
    name = forms.CharField(max_length=255,required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Name'}),label='Full Name')
   
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Email'}),required=True,label='Email')
    
    contact = forms.CharField(max_length=10,help_text=' Enter Mobile Number',
        validators=[RegexValidator(regex='^[9876]\d{9}$')],widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Mobile Number'}))
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Your Message'}),required=True,label='Message')