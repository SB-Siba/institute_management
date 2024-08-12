from django.shortcuts import render, redirect
from django.views import View
from app_common import forms
from users.forms import LoginForm
from product.models import Category,Products,SimpleProduct,ImageGallery
from django.conf import settings
from django.db.models import Prefetch
app = "app_common/"


# static pages 


class HomeView(View):
    template = app + "landing_page.html"

    def get(self, request):
        categories = Category.objects.all()
        new_products = Products.objects.filter(show_as_new="yes").prefetch_related(
            Prefetch('simpleproduct_set', queryset=SimpleProduct.objects.prefetch_related('image_gallery'))
        )

        
        context = {
            'categories': categories,
            'new_products': new_products,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template, context)


class AboutUs(View):
    template = app + "about_us.html"

    def get(self, request):
       
        return render(request, self.template)


class ContactSupportView(View):
    contact_template = app + 'contact_us.html'
    support_template = app + 'support.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() if request.user.get_full_name() else '',
                'email': request.user.email if request.user.email else '',
                'contact': getattr(request.user.profile, 'contact', '') if hasattr(request.user, 'profile') else '',
            }
            template = self.support_template
        else:
            initial_data = {
                'name': '',
                'email': '',
                'contact': '',
            }
            template = self.contact_template

        form = ContactMessageForm(initial=initial_data)
        return render(request, template, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                contact=form.cleaned_data['contact'],
                message=form.cleaned_data['message'],
            )
            if request.user.is_authenticated:
                messages.success(request, 'Your support request has been sent successfully.')
                return redirect('app_common:contact_support')  # Redirect to the same URL pattern
            else:
                messages.success(request, 'Your message has been sent successfully.')
                return redirect('app_common:contact_support')  # Redirect to the same URL pattern
        else:
            # Render the same template but with errors
            template = self.support_template if request.user.is_authenticated else self.contact_template
            return render(request, template, {'form': form})

class TermsConditions(View):
    template = app + "terms_conditions.html"

    def get(self, request):
       
        return render(request, self.template)

class PrivacyPolicy(View):
    template = app + "privacy_policy.html"

    def get(self, request):
       
        return render(request, self.template)

class ReturnPolicy(View):
    template = app + "return_policy.html"

    def get(self, request):
       
        return render(request, self.template)

class OurServices(View):
    template = app + "our_services.html"

    def get(self, request):
       
        return render(request, self.template)
