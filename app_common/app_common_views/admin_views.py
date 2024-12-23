from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from app_common.models import ContactMessage
from app_common.forms import ReplyForm
from users.models import Support
from users.user_views.emails import send_template_email
from itertools import chain

app = 'app_common/'


class AdminMessageListView(View):
    template = app + 'admin/message_list.html'

    def get(self, request, *args, **kwargs):
        contact_messages = ContactMessage.objects.all().order_by('-created_at')
        support_messages = Support.objects.all().order_by('-created_at')

        # Add a `type` attribute to each message
        for message in contact_messages:
            message.type = 'contact'
        for message in support_messages:
            message.type = 'support'

        # Combine both message types, sorted by created_at
        messages_list = sorted(
            chain(contact_messages, support_messages),
            key=lambda message: message.created_at,
            reverse=True
        )

        return render(request, self.template, {'messages': messages_list})


class AdminMessageDetailView(View):
    template = app + 'admin/message_detail.html'

    def get(self, request, message_id, *args, **kwargs):
        message_type = request.GET.get('type', 'contact')

        # Get the message object based on the type (contact or support)
        if message_type == 'contact':
            message = get_object_or_404(ContactMessage, id=message_id)
        else:
            message = get_object_or_404(Support, id=message_id)

        # If the user is authenticated, check if the message belongs to the user
        if request.user.is_authenticated and message.user == request.user:
            # Optionally, you can fetch authenticated user messages here
            pass

        # Pass the message and message type to the template
        return render(request, self.template, {
            'message': message,
            'type': message_type
        })

    def post(self, request, message_id, *args, **kwargs):
        message_type = request.GET.get('type', 'contact')

        if message_type == 'contact':
            message = get_object_or_404(ContactMessage, id=message_id)
        else:
            message = get_object_or_404(Support, id=message_id)

        # Handle the form submission or redirection here
        return HttpResponseRedirect(reverse('app_common:admin_message_list'))


class AdminMessageDeleteView(View):
    def post(self, request, message_id, *args, **kwargs):
        message_type = request.GET.get('type', 'contact')
        if message_type == 'contact':
            message = get_object_or_404(ContactMessage, id=message_id)
        else:
            message = get_object_or_404(Support, id=message_id)

        message.delete()
        messages.success(request, "Message deleted successfully.")
        return redirect('app_common:admin_message_list')


class AdminMessageBulkDeleteView(View):
    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist('selected_messages')
        message_type = request.POST.get('message_type')

        if selected_ids:
            if message_type == 'contact':
                ContactMessage.objects.filter(id__in=selected_ids).delete()
            elif message_type == 'support':
                Support.objects.filter(id__in=selected_ids).delete()

            messages.success(request, "Selected messages deleted successfully.")
        else:
            messages.warning(request, "No messages selected for deletion.")
        return redirect('app_common:admin_message_list')
