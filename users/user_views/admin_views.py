from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from helpers import utils
from users import models,forms

app = "users/admin/"

# admin dashboard and manage users list

@method_decorator(utils.super_admin_only, name='dispatch')
class AdminDashboard(View):
    template = app + "index.html"  # Update the template path if necessary

    def get(self, request):
        return render(request, self.template)


class UserList(View):
    model = models.User
    template = app + "user_list.html"

    def get(self,request):
        user_obj = self.model.objects.filter(is_superuser=False).order_by("id")
        return render(request,self.template,{"user_obj":user_obj})




class AddUserView(View):
    template = app + "user_add.html"
    form_class = forms.AddUserForm
    def get(self, request):
        form = self.form_class()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Ensure the password is hashed
            user.save()
            messages.success(request, f"User {user.full_name} has been successfully added.")
            return redirect('users:userslist')
        messages.error(request, "There was an error adding the user. Please check the details and try again.")
        return render(request, self.template, {'form': form})


class DeleteUser(View):
    model = models.User
    template = app + "confirm_delete.html"  # A template to confirm deletion

    def get(self, request, user_id):
        user = get_object_or_404(self.model, id=user_id)
        return render(request, self.template, {"user": user})

    def post(self, request, user_id):
        user = get_object_or_404(self.model, id=user_id)
        user.delete()
        messages.success(request, f"User {user.full_name} has been successfully deleted.")
        return redirect('users:userslist')


class UserDetailView(View):
    model = models.User
    template = app + "user_profile.html"
    def get(self,request,user_id):
        user_obj = self.model.objects.get(id=user_id)
        return render(request, self.template, {"user_obj": user_obj})

class Edit_User(View):
    template = app + "edit_user.html"
    def get(self,request,user_id):
        user =models.User.objects.get(pk = user_id)
        form = forms.EditUserForm()
        form.fields['email'].initial = user.email
        form.fields['full_name'].initial = user.full_name
        form.fields['contact'].initial = user.contact


        data = {
            'form':form,
            'id':user_id,
            'username':user.email,

        }
        return render(request,self.template,data)
    def post(self,request,user_id):
        user = models.User.objects.get(pk = user_id)

        form = forms.EditUserForm(request.POST)
        if form.is_valid:
            email = request.POST.get("email")
            full_name = request.POST.get("full_name")
            contact = request.POST.get("contact")

            user.email = email
            user.full_name = full_name
            user.contact = contact
            user.save()

        return redirect("users:user_detail",user_id)