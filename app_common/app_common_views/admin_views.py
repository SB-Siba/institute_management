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
        messages = sorted(
            chain(contact_messages, support_messages),
            key=lambda message: message.created_at,
            reverse=True
        )

        return render(request, self.template, {'messages': messages})

class AdminMessageDetailView(View):
    template = app +'admin/message_detail.html'

    def get(self, request, message_id, *args, **kwargs):
        message_type = request.GET.get('type', 'contact')
        if message_type == 'contact':
            message = get_object_or_404(ContactMessage, id=message_id)
        else:  # Handle Support messages
            message = get_object_or_404(Support, id=message_id)

        form = ReplyForm()
        return render(request, self.template, {'message': message, 'type': message_type, 'form': form})

    def post(self, request, message_id, *args, **kwargs):
        message_type = request.GET.get('type', 'contact')
        if message_type == 'contact':
            message = get_object_or_404(ContactMessage, id=message_id)
        else:
            message = get_object_or_404(Support, id=message_id)

        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.cleaned_data['reply']
            context = {
                'user_name': message.name if message_type == 'contact' else message.user.full_name,
                'reply_message': reply,
            }
            send_template_email(
                subject='Reply to Your Message',
                template_name='users/email/contact_message_reply.html',
                context=context,
                recipient_list=[message.email]
            )
            messages.success(request, 'Reply sent successfully.')
            return redirect('app_common:admin_message_list')

        return render(request, self.template, {'message': message, 'type': message_type, 'form': form})
    

class AdminMessageDeleteView(View):
    def post(self, request, message_id, *args, **kwargs):
        message = get_object_or_404(ContactMessage, id=message_id)
        message.delete()
        messages.success(request, "Message deleted successfully.")
        return redirect('app_common:admin_message_list')
