from datetime import timedelta
from django.shortcuts import render, redirect , HttpResponse
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
import json
from django.contrib import messages
from django.contrib import auth
from users.forms import SignUpForm,LoginForm,ForgotPasswordForm,ResetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import logout,login,authenticate
from users import models
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.generic.edit import FormView
from users import forms
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.views.generic.edit import FormView
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.timezone import now
from users.user_views.emails import send_template_email

app = "users/"

# authentications
class Registration(View):
    model = models.User
    template = app + 'authtemp/registration.html'

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            full_name = form.cleaned_data.get('full_name')

            try:
                new_user = self.model(username=username, full_name=full_name, is_admitted=False)
                new_user.set_password(password)
                new_user.save()
                new_user_login = authenticate(request, username=username, password=password)
                if new_user_login is not None:
                    login(request, new_user_login)
                    
                    # context = {
                    #     'full_name': full_name,
                    #     'username': username,
                    # }

                    # send_template_email(
                    #     subject='Registration Confirmation',
                    #     template_name='users/email/register_email.html',
                    #     context=context,
                    #     recipient_list=[username]
                    # )
                    
                    messages.success(request, "Registration successful! You are now logged in.")
                    return redirect('users:login')
                else:
                    messages.error(request, "Authentication failed. Please try again.")
            except Exception as e:
                print(e)
                messages.error(request, 'Something went wrong while registering your account. Please try again later.')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, self.template, {'form': form})


class Login(View):
    model = models.User
    template_name = app + "authtemp/login.html"

    def get(self, request):
        form = LoginForm()
        form2 = ForgotPasswordForm()  # Include ForgotPasswordForm for the modal
        return render(request, self.template_name, {'form': form, 'form2': form2})
    
    def post(self, request):
        form = LoginForm(request.POST)
        form2 = ForgotPasswordForm()  # Include ForgotPasswordForm for the modal
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Log in the user
                if user.is_superuser:
                    return redirect('users:admin_dashboard')
                else:
                    return redirect('users:home')
            else:
                messages.error(request, "Invalid username or password")
        
        return render(request, self.template_name, {'form': form, 'form2': form2})

class Logout(View):
    template_name = app +'authtemp/logout_confirmation.html'
    def get(self, request, *args, **kwargs):
        if 'confirm' in request.GET:
            logout(request)
            return redirect('users:home')
        
        if 'cancel' in request.GET:
            if request.user.is_superuser:
                return redirect('users:admin_dashboard')
            return redirect('users:home')

        return render(request, self.template_name)

class ForgotPasswordView(View):
    def post(self, request):
        form2 = ForgotPasswordForm(request.POST)
        if form2.is_valid():
            email = form2.cleaned_data['email']
            try:
                user = models.User.objects.get(email=email)
                # Generate the password reset token
                token = user.generate_reset_password_token()
                reset_link = f"{settings.SITE_URL}/reset_password/{token}/"

                # Email context and sending logic
                context = {
                    'full_name': user.full_name,
                    'reset_link': reset_link,
                }
                send_template_email(
                    subject='Reset Your Password',
                    template_name='users/email/reset_password_email.html',
                    context=context,
                    recipient_list=[email]
                )
                messages.success(request, "Password reset email sent successfully.")
            except models.User.DoesNotExist:
                messages.warning(request, "No account found with that email address.")
        else:
            messages.error(request, "Invalid email address. Please try again.")

        return redirect('users:login')

class ResetPasswordView(View):
    template_name = app + 'authtemp/reset_password.html'

    def get(self, request, token):
            form = forms.ResetPasswordForm()
            return render(request, self.template_name, {'form': form, 'token': token})
        
    def post(self, request, token):
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password != confirm_password:
                return HttpResponse("Passwords do not match.")
            try:
                user = models.User.objects.get(token=token)
                if user:
                    user.set_password(new_password)
                    user.token = None
                    user.save()
                    messages.success(request, "Password reset successfully.")
                    return redirect('users:login')
                else:
                    return HttpResponse("Token has expired or is invalid.")
            except models.User.DoesNotExist:
                return HttpResponse("Invalid token.")
        return render(request, self.template_name, {'form': form})



class AccountDeletionView(LoginRequiredMixin, View):
    template_name = app + 'authtemp/account_deletion.html'  # Adjust the path as necessary

    def get(self, request, *args, **kwargs):
        user = request.user
        days_remaining = (user.deletion_date - timezone.now()).days if user.deletion_requested else None
        return render(request, self.template_name, {'user': user, 'days_remaining': days_remaining})

    def post(self, request, *args, **kwargs):
        user = request.user

        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'cancel_deletion' and user.deletion_requested:
                user.cancel_deletion()
                messages.success(request, "Account deletion canceled.")
                return JsonResponse({'success': True, 'message': 'Account deletion canceled.'})

            elif action == 'request_deletion' and not user.deletion_requested:
                user.request_deletion()
                messages.success(request, "Your account will be deleted in 30 days.")
                return JsonResponse({'success': True, 'message': 'Your account will be deleted in 30 days.'})

            else:
                return JsonResponse({'success': False, 'message': 'Invalid action or state.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)