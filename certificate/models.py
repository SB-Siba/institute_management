from django.db import models
from course.models import Course
from users.models import Batch, User

class AppliedCertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} in {self.batch}"
    
class CertificateDesign(models.Model):
    applied_certificate = models.OneToOneField(AppliedCertificate, on_delete=models.CASCADE)
    design_file = models.FileField(upload_to='certificates/')  # Assuming file upload for the designed certificate
    designed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.applied_certificate.user}"