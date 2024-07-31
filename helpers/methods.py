from django.utils import timezone
from datetime import timedelta


def request_deletion(self):
        """Request account deletion."""
        self.deletion_requested = True
        self.deletion_date = timezone.now() + timedelta(days=30)
        self.save()

def cancel_deletion(self):
        """Cancel account deletion."""
        self.deletion_requested = False
        self.deletion_date = None
        self.save()


        