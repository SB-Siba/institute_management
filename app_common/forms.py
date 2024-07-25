from django import forms
from . import models


class ContactMessageForm(forms.Form):
    name = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Name'}),
        label='Full Name'
        
    )
   
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Email'}),
        required=True,
        label='Email'
    )
   
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Your Message'}),
        required=True,
        label='Message'
    )