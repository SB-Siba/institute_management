from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from app_common.models import ContactMessage
from app_common.forms import ReplyForm
from users.user_views.emails import send_template_email


app = 'app_common/'

class AdminMessageListView(View):
    template = app +'admin/message_list.html'

    def get(self, request, *args, **kwargs):
        messages = ContactMessage.objects.all().order_by('-created_at')
        return render(request, self.template, {'messages': messages})

class AdminMessageDetailView(View):
    template = app +'admin/message_detail.html'

    def get(self, request, message_id, *args, **kwargs):
        message = get_object_or_404(ContactMessage, id=message_id)
        form = ReplyForm()
        return render(request, self.template, {'message': message, 'form': form})

    def post(self, request, message_id, *args, **kwargs):
        message = get_object_or_404(ContactMessage, id=message_id)
        form = ReplyForm(request.POST)

        if form.is_valid():
            reply = form.cleaned_data['reply']

            # Send the reply via email using the template function
            context = {
                'user_name': message.name,
                'reply_message': reply,
            }
            send_template_email(
                subject='Reply to Your Contact Message',
                template_name='users/email/contact_message_reply.html',
                context=context,
                recipient_list=[message.email]
            )

            messages.success(request, 'Reply sent successfully.')
            return redirect('app_common:admin_message_list')

        return render(request, self.template, {'message': message, 'form': form})
