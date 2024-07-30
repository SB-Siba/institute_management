from celery import shared_task
from django.utils import timezone
from .models import User

@shared_task
def delete_expired_accounts():
    now = timezone.now()
    expired_users = User.objects.filter(deletion_requested=True, deletion_date__lte=now)
    
    for user in expired_users:
        user.delete()
