from django.shortcuts import render, redirect
from datetime import datetime
from django.conf import settings
from django.views import View
from django.contrib import messages
from users import forms
from users import models
from uuid import uuid4

app = "users"


class HomeView(View):
    template =  "users/user/home.html"
    un_template = "app_common/landing_page.html"
    def get(self, request):
        user = request.user
        if not user.is_authenticated:

            return render(request, self.un_template, locals())
            
        return render(request, self.template, locals())

class ProfileView(View):
    template = app + "user/userprofile.html"

    def get(self, request):
        user = request.user
        print(user)
       
        userobj = models.User.objects.get(email=user.email)
        try:
            profileobj = models.User.objects.get(user=userobj)
        except User.DoesNotExist:
            profileobj = None

        if not user.is_authenticated:
            return redirect("users:login")

        return render(request, self.template, locals())


class UpdateProfileView(View):
    template = app + "user/update_profile.html"
    form = forms.UpdateProfileForm

    def get(self, request):
        user = request.user
        
        userobj = models.User.objects.get(email=user.email)
        print(userobj)
    
        profileObj, created = models.User.objects.get_or_create(user=userobj)
       
        print(profileObj)
        initial_data = {
            "email": userobj.email,
            "full_name": userobj.full_name,
            "contact": userobj.contact,
            "bio": profileObj.bio,
            "profile_pic": profileObj.profile_pic,
        }
        form = self.form(initial=initial_data)

        return render(request, self.template, locals())

    def post(self, request):
        # category_obj = Category.objects.all()
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            full_name = form.cleaned_data["full_name"]
            contact = form.cleaned_data["contact"]
            bio = form.cleaned_data["bio"]
            profile_picture = form.cleaned_data["profile_pic"]
            password = form.cleaned_data["password"]

            user = request.user

            try:
                userobj = User.objects.get(email=user.email)
                userobj.email = email
                userobj.full_name = full_name
                userobj.contact = contact

                profile_object = models.User.objects.filter(user=user)

                if profile_picture is None:
                    picture = ""
                    for i in profile_object:
                        picture = i.profile_pic
                else:
                    picture = profile_picture

                if len(profile_object) == 0:
                    profileobj = models.User(user=user, bio=bio, profile_pic=picture)
                    profileobj.save()
                else:
                    for i in profile_object:
                        i.user = user
                        i.profile_pic = picture
                        i.bio = bio
                        i.save()

                if len(password) > 0:
                    userobj.set_password(password)
                    messages.success(request, "Password Changed Successfully")

                userobj.save()
                return redirect("users:userprofile")

            except:
                messages.error(request, "Error in Updating Profile")
        return render(request, self.template, locals())




class AllAddress(View):
    template = app + "user/alladdress.html"

    def get(self, request):
        user = request.user
        address = user.address or []  # This will return a list of addresses

        return render(request, self.template, {"address": address})



class AddAddress(View):
    template = app + "user/addaddress.html"
    form = forms.AddressForm

    def get(self, request):
        form = self.form()
        return render(request, self.template, locals())

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            landmark1 = form.cleaned_data["landmark1"]
            landmark2 = form.cleaned_data["landmark2"]
            country = form.cleaned_data["country"]
            state = form.cleaned_data["state"]
            city = form.cleaned_data["city"]
            zipcode = form.cleaned_data["zipcode"]

            address_id = str(uuid4())

            address_data = {
                "id": address_id,
                "landmark1": landmark1,
                "landmark2": landmark2,
                "country": country,
                "state": state,
                "city": city,
                "zipcode": zipcode,
            }

            user = request.user
            addresses = user.address or []

            # Append the new address data to the list of addresses
            addresses.append(address_data)

            # Save the updated list of addresses back to the user model
            user.address = addresses
            user.save()

            return redirect("users:alladdress")
        else:
            return redirect("users:addaddress")


class DeleteAddress(View):
    def get(self, request, address_id):
        user = request.user
        addresses = user.address or []

        # Filter out the address with the specified ID
        addresses = [
            address for address in addresses if address.get("id") != address_id
        ]

        # Update the user model with the modified list of addresses
        user.address = addresses
        user.save()

        return redirect("users:alladdress")