from django.urls import path
from certificate.certificate_view import admin_view

app_name = 'certificate'

urlpatterns = [
    path('exam-results/', admin_view.AllExamResultsView.as_view(), name='exam_results'),
    path('designed-certificate/', admin_view.DesignedCertificateView.as_view(), name='designed_certificate'),
]
