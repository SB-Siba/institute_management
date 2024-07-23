from django.shortcuts import render, redirect , HttpResponse
from django.views import View
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

app = "users/"


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
            confirm_password = form.cleaned_data.get('confirm_password')
            full_name = form.cleaned_data.get('full_name')

            user = auth.authenticate(request, username=email, password=password)
            if user is None:
                try:
                    if password == confirm_password:
                        new_user = self.model(email=email, full_name=full_name, contact=contact)
                        new_user.set_password(password)
                        try:
                            user_email = email
                            subject = "Registration Successful."
                            message = f"""\
                            Dear {full_name},
                            Your account has been created successfully on our site. You can login now."""
                            from_email = "noreplyf577@gmail.com"
                            send_mail(subject, message, from_email, [user_email], fail_silently=False)

                            new_user.save()
                            messages.success(request, 'Registration Successful!')
                            
                            # Auto login the user
                            login(request, new_user)
                            return redirect('users:home')
                        except Exception as e:
                            print("Error in sending verification mail", e)
                            messages.error(request, 'Email could not be sent due to some error. Please contact support for further assistance.')
                            return redirect('users:signup')
                    else:
                        messages.error(request, "Password does not match with Confirm Password")
                        return redirect('users:signup')
                except Exception as e:
                    print(e)
                    messages.error(request, 'Something went wrong while registering your account. Please try again later.')
            else:
                messages.error(request, "User already exists.")
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
            return UserModel._default_manager.get(pk=uid)
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



class AccountDeletionRequestView(LoginRequiredMixin, View):
    template_name = app +'authtemp/account_deletion.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        return render(request, self.template_name, {'user': user})

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.deletion_requested:
            user.request_deletion()
            messages.success(request, "Your account is scheduled for deletion in 30 days.")
        return redirect('account_deletion_status')

class AccountDeletionStatusView(LoginRequiredMixin, View):
    template_name = app + 'authtemp/account_deletion_status.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        days_remaining = (user.deletion_date - timezone.now()).days if user.deletion_requested else None
        return render(request, self.template_name, {'user': user, 'days_remaining': days_remaining})

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'cancel_deletion' in request.POST and user.deletion_requested:
            user.cancel_deletion()
            messages.success(request, "Account deletion canceled.")
        return redirect('account_deletion_status')
    def post(self, request):
        user = request.user
        user.cancel_account_deletion()
        messages.success(request, "Your account deletion request has been canceled.")
        return redirect('account-deletion-request')