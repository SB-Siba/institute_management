from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from helpers import utils


app = "app_common/"

@method_decorator(utils.super_admin_only, name='dispatch')
class AdminDashboard(View):
    template = app + "admin/index.html"  # Update the template path if necessary

    def get(self, request):
        return render(request, self.template)