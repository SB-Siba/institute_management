from django.shortcuts import render, redirect
from django.views import View
from app_common import forms
from users.forms import LoginForm
from product.models import Category,Products
from django.conf import settings
app = "app_common/"


# static pages 


class HomeView(View):
    template = app + "landing_page.html"

    def get(self, request):
        # Fetch the first 6 categories to display on the home page
        categories = Category.objects.all()
        trending_products = Products.objects.filter(trending="yes")
        new_products = Products.objects.filter(show_as_new="yes")

        
        context = {
            'categories': categories,
            'trending_products': trending_products,
            'new_products': new_products,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template, context)


class AboutUs(View):
    template = app + "about_us.html"

    def get(self, request):
       
        return render(request, self.template)


class ContactUs(View):
    template = 'shoppingsite/contact_us.html'  # Adjust the template path as needed

    def get(self, request):
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.full_name if request.user.full_name else '',
                'email': request.user.email if request.user.email else '',
                'mobile_no': request.user.contact if request.user.contact else '',
            }
        else:
            initial_data = {
                'full_name': '',
                'email': '',
                'mobile_no': '',
            }
        form = forms.ContactMessageForm(initial=initial_data)
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = forms.ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('shoppingsite:contact_us')  
        return render(request, self.template, {'form': form})

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
