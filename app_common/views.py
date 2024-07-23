from django.shortcuts import render, redirect
from django.views import View
from . import forms
app = "app_common/"


class AboutPage(View):
    template = app + "about.html"

    def get(self,request):
        
        return render(request,self.template)



def get_rand_number(length=5):
    return ''.join(random.choices(string.digits, k=length))
class contactMesage(View):
    template = app + "contact_page.html"
 
    def get(self, request):
        if request.user.is_authenticated:
            initial = {'user': request.user.full_name , 'email': request.user.email}
            template = app + "contact_page.html"    
        else:
            initial = {}
            template = app + "contact_page_unauthenticated.html"
 
        form = forms.ContactMessageForm(initial=initial)
        context = {"form": form}
        return render(request, template, context)
 
    def post(self, request):
        form = forms.ContactMessageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            name = form.cleaned_data.get('name')
            email = form.cleaned_data['email']
            query_message = form.cleaned_data['message']
            try:
                if request.user.is_authenticated:
                    u_obj = request.user
                    contact_obj = ContactMessage(user=u_obj, message=query_message)
                else:
                    contact_obj = ContactMessage(uid=get_rand_number(5), message=query_message, reply=email)

                contact_obj.save()
 
                subject = "Your Query Received."
                message = f"Dear {name or email},\nYour query has been received successfully.\nOur team members will look into this."
                message = f"Dear {name or email},\nYour query has been received successfully.\nOur team members will look into this."
                from_email = "forverify.noreply@gmail.com"
                send_mail(subject, message, from_email, [email], fail_silently=False)
 
                if request.user.is_authenticated:
                    messages.info(request, "Your message has been sent successfully.")
                else:
                    messages.info(request, "Your message has been received. You can log in to track the response.")
               
                return redirect("user:contactmessage")
            except Exception as e:
                print(f"Exception: {e}")
                print(f"Exception: {e}")
                messages.warning(request, "There was an error while sending your message.")
                return self.get(request)
                return self.get(request)
        else:
            # Print form errors to the console for debugging
            print(f"Form errors: {form.errors}")
            # Print form errors to the console for debugging
            print(f"Form errors: {form.errors}")
            messages.warning(request, "Invalid form data. Please correct the errors.")
            return self.get(request)