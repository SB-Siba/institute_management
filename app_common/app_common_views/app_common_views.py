from django.shortcuts import render, redirect
from django.views import View
from app_common import forms
app = "app_common/"


# static pages 

class HomeView(View):
    template =  "users/user/home.html"
    un_template = app + "landing_page.html"
    def get(self, request):
        user = request.user
        if not user.is_authenticated:

            return render(request, self.un_template, locals())
            
        return render(request, self.template, locals())


class AboutPage(View):
    template = app + "about.html"

    def get(self,request):
        
        return render(request,self.template)


class Contact(View):
    template = app + "about.html"

    def get(self,request):
        
        return render(request,self.template)

class TermsAndCondtion(View):
    template = app + "about.html"

    def get(self,request):
        
        return render(request,self.template)

class PrivacyPolicy(View):
    template = app + "about.html"

    def get(self,request):
        
        return render(request,self.template)

class AboutPage(View):
    template = app + "about.html"

    def get(self,request):
        
        return render(request,self.template)