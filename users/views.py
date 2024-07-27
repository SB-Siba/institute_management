from django.shortcuts import render, redirect , HttpResponse
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
import json
from django.contrib import messages
from django.contrib import auth
from users.forms import SignUpForm,LoginForm,CustomPasswordResetForm,CustomSetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import logout,login,authenticate
from users import models
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse_lazy
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
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            contact = form.cleaned_data.get('contact')
            full_name = form.cleaned_data.get('full_name')

            try:
                new_user = self.model(email=email, full_name=full_name, contact=contact)
                new_user.set_password(password)
                new_user.save()
                new_user_login = authenticate(request, username=email, password=password)
                if new_user_login is not None:
                    login(request, new_user_login)
                    
                    # Send registration success email
                    send_mail(
                        'Registration Successful',
                        f'Hello {full_name},\n\nYour registration was successful! You are now logged in.\n\nThank you for registering with us.',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    
                    messages.success(request, "Registration successful! You are now logged in.")
                    return redirect('users:home')
                else:
                    messages.error(request, "Authentication failed. Please try again.")
            except Exception as e:
                print(e)
                messages.error(request, 'Something went wrong while registering your account. Please try again later.')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, self.template, {'form': form})


class Login(View):
    model=models.User
    template = app + "authtemp/login.html"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                user = models.User.objects.get(email=email)
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('users:admin_dashboard')
                    else:
                        return redirect('users:home')
                else:
                    messages.error(request, "Incorrect password")
            except models.User.DoesNotExist:
                messages.error(request, "Invalid email")
        
        return render(request, self.template, {'form': form})

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('users:home')

class LogoutConfirmationView(View):
    template_name = app +'authtemp/logout_confirmation.html'

    def get(self, request):
        return render(request, self.template_name)


class CancelLogoutView(View):
    def get(self, request):
    
        if request.user.is_superuser:
            return redirect('users:admin_dashboard')

        return redirect('users:home')


class CustomPasswordResetView(FormView):
    template_name = app + "authtemp/password_reset.html"
    template_email = app + "authtemp/password_reset_email.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("users:password_reset_done")
    token_generator = default_token_generator

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        users = models.User.objects.filter(email=email)
        if users.exists():
            for user in users:
                current_site = get_current_site(self.request)
                mail_subject = "Password reset link"
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = self.token_generator.make_token(user)
                reset_link = reverse_lazy(
                    "users:password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
                reset_url = f"{self.request.scheme}://{current_site.domain}{reset_link}"
                html_message = render_to_string(
                    self.template_email,
                    {
                        "user": user,
                        "reset_url": reset_url,
                    },
                )
                text_message = strip_tags(html_message)
                msg = EmailMultiAlternatives(
                    mail_subject, text_message, "admin@example.com", [email]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send()
        return super().form_valid(form)
 
 
class CustomPasswordResetDoneView(TemplateView):
    template_name = app + "authtemp/password_reset_done.html"
    UserModel = get_user_model()
 
 
class CustomPasswordResetConfirmView(FormView):
    template_name = app + "authtemp/password_reset_confirm.html"
    form_class = CustomSetPasswordForm
    token_generator = default_token_generator
    success_url = reverse_lazy("users:password_reset_complete")

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs["uidb64"])
        if self.user is not None and self.is_token_valid(self.user, kwargs["token"]):
            return super().dispatch(request, *args, **kwargs)
        return render(request, self.template_name, {"validlink": False})

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            return models.User._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            UserModel.DoesNotExist,
            ValidationError,
        ):
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def is_token_valid(self, user, token):
        try:
            return self.token_generator.check_token(user, token)
        except:
            pass
        return False
    
class CustomPasswordResetCompleteView(TemplateView):
    template_name = app + "authtemp/password_reset_complete.html"



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
                user.cancel_deletion()  # Call the cancel_deletion method
                messages.success(request, "Account deletion canceled.")
                return JsonResponse({'success': True, 'message': 'Account deletion canceled.'})

            elif action == 'request_deletion' and not user.deletion_requested:
                user.request_deletion()  # Call the request_deletion method
                messages.success(request, "Your account will be deleted in 30 days.")
                return JsonResponse({'success': True, 'message': 'Your account will be deleted in 30 days.'})

            else:
                return JsonResponse({'success': False, 'message': 'Invalid action or state.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)