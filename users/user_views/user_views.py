from base64 import b64encode
import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
from django.conf import settings
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
import qrcode
from course.models import Course
from certificate.models import ApprovedCertificate
from users import forms
from users.models import Payment, User
from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum


app = "users/user/"

class ProfileView(View):
    template = app + "userprofie.html"

    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return redirect("users:login")

        return render(request, self.template, locals())

class AllAddress(View):
    template = app + "alladdress.html"

    def get(self, request):
        user = request.user
        addresses = user.address or []  # This will return a list of addresses

        return render(request, self.template, {"addresses": addresses})

class ProfileAddAddress(View):
    template = app + "addaddress.html"
    form = forms.AddressForm

    def get(self, request):
        form = self.form()
        return render(request, self.template, locals())

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            Address1 = form.cleaned_data["Address1"]
            Address2 = form.cleaned_data["Address2"]
            country = form.cleaned_data["country"]
            state = form.cleaned_data["state"]
            city = form.cleaned_data["city"]
            mobile_no = form.cleaned_data["contact"]
            pincode = form.cleaned_data["pincode"]

            address_id = str(uuid4())

            address_data = {
                "id": address_id,
                "Address1": Address1,
                "Address2": Address2,
                "country": country,
                "state": state,
                "city": city,
                'mobile_no':mobile_no,
                "pincode": pincode,
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

class ProfileUpdateAddress(View):
    template = app + "update_address.html"
    form = forms.AddressForm

    def get(self, request, address_id):
        user = request.user
        addresses = user.address or []
        address = next((addr for addr in addresses if addr["id"] == address_id), None)
        
        if not address:
            messages.error(request, "Address not found.")
            return redirect("users:alladdress")

        form = self.form(initial=address)
        return render(request, self.template, {'form': form, 'address_id': address_id})

    def post(self, request, address_id):
        form = self.form(request.POST)
        if form.is_valid():
            user = request.user
            addresses = user.address or []

            # Find the existing address
            address_index = next((index for (index, addr) in enumerate(addresses) if addr["id"] == address_id), None)

            if address_index is None:
                messages.error(request, "Address not found.")
                return redirect("users:alladdress")

            address_data = {
                "id": address_id,
                "Address1": form.cleaned_data["Address1"],
                "Address2": form.cleaned_data["Address2"],
                "country": form.cleaned_data["country"],
                "state": form.cleaned_data["state"],
                "city": form.cleaned_data["city"],
                "mobile_no": form.cleaned_data["contact"],
                "pincode": form.cleaned_data["pincode"],
            }

            # Update the address in the list
            addresses[address_index] = address_data

            # Save the updated list of addresses back to the user model
            user.address = addresses
            user.save()

            messages.success(request, "Address updated successfully.")
            return redirect("users:alladdress")
        else:
            messages.error(request, "Invalid address form. Please correct the errors below.")
            return render(request, self.template, {'form': form, 'address_id': address_id})
        
class ProfileDeleteAddress(View):
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

class DashboardView(View):
    template = app + "index.html"

    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return redirect("users:login")

        # Fetch the admitted course
        enrolled_course = user.course_of_interest  # Assuming this is the admitted course

        # Initialize fees-related variables
        total_fees = 0
        paid_fees = 0
        balance_fees = 0

        if enrolled_course:
            # Fetch total fees from the course
            total_fees = enrolled_course.course_fees if enrolled_course.course_fees else 0

            # Calculate paid fees
            paid_fees = Payment.objects.filter(student=user, course=enrolled_course).aggregate(Sum('amount'))['amount__sum'] or 0

            # Calculate balance fees
            balance_fees = total_fees - paid_fees

        # Fetch approved certificates
        applications = ApprovedCertificate.objects.filter(user=user)

        context = {
            'userobj': user,
            'course': enrolled_course,
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'balance_fees': balance_fees,
            'applications': applications,
        }

        return render(request, self.template, context)

class UpdateProfileView(UpdateView):
    model = User
    form_class = forms.ProfileUpdateForm
    template_name = app + 'profile_update.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating your profile. Please try again.")
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class SupportView(View):
    template_name = app + 'help_support.html'

    def get(self, request):
        form = forms.SupportForm(initial={
            'mobile': request.user.contact,
            'email': request.user.email
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login') 

        form = forms.SupportForm(request.POST, request.FILES)
        if form.is_valid():
            support = form.save(commit=False)
            support.user = request.user  
            support.save()
            messages.success(request, 'Your support request has been submitted successfully.')
            return redirect('users:support')
        return render(request, self.template_name, {'form': form})
    
class MyCoursesView(View):
    template_name = app + 'my_course.html'

    def get(self, request, *args, **kwargs):
        # Handle GET request
        user = request.user
        context = {
            'student_image':user.student_image.url if user.student_image else None,
            'student_signature':user.student_signature.url if user.student_signature else None,
            'course': user.course_of_interest,
            'roll_number': user.roll_number,
            'abbreviation': user.abbreviation,
            'full_name': user.full_name,
            'select_one': user.select_one,
            'father_husband_name': user.father_husband_name,
            'course_fees': user.course_fees,
            'fees_received': user.fees_received,
            'balance': user.balance,
            'gender': user.gender
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle POST request (e.g., user submits updates or actions)
        action = request.POST.get('action')
        
        if action == "update_fees":
            new_fees = request.POST.get('fees_received')
            if new_fees:
                try:
                    # Update fees received and balance for the user
                    user = request.user
                    user.fees_received = float(new_fees)
                    user.balance = user.course_fees - user.fees_received
                    user.save()
                    return HttpResponse("Fees updated successfully!")
                except ValueError:
                    return HttpResponse("Invalid data provided!", status=400)
        
        return HttpResponse("Unhandled POST action!", status=400)
    
class AdmissionFormView(View):
    template_name = 'users/admin/students_details.html'

    def get(self, request, course_id):
        # Fetch the logged-in user (assuming you want the currently logged-in user's details)
        student = get_object_or_404(User, id=request.user.id)

        # Fetch the course details
        course = get_object_or_404(Course, id=course_id)

        # Prepare data to encode in the QR code
        student_data = {
            "id": student.pk,
            "name": student.full_name,  # Use full_name instead of combining first_name and last_name
            "email": student.email,
            "phone": student.contact if hasattr(student, 'contact') else "N/A",
        }
        
        # Convert data to QR code content (e.g., JSON)
        qr_data_string = str(student_data)
        
        # Generate the QR code
        qr = qrcode.make(qr_data_string)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        
        # Convert QR code to base64 to render in HTML
        qr_data = b64encode(buffer.getvalue()).decode()
        qr_image = f"data:image/png;base64,{qr_data}"

        # Pass data to the template
        context = {
            'student': student,
            'course': course,
            'qr_image': qr_image,
        }
        return render(request, self.template_name, context)