from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.contrib import messages

app = "app_common/user/"

class HomeView(View):
    template = app + "home1.html"
    un_template = app + "landing_page.html"
    def get(self, request):
        user = request.user
        if not user.is_authenticated:

            return render(request, self.un_template, locals())
            
        return render(request, self.template, locals())