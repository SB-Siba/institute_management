from django.urls import path
from certificate.certificate_view import admin_view

app_name = 'certificate'

urlpatterns = [
    path('exam-results/', admin_view.AllExamResultsView.as_view(), name='exam_results'),
    path('designed-certificate/', admin_view.DesignedCertificateView.as_view(), name='designed_certificate'),
    path('apply-certificate/', admin_view.ApplyCertificateView.as_view(), name='apply_certificate'),
    path('applied-certificates/', admin_view.AppliedCertificateListView.as_view(), name='applied_certificates'),  # This uses underscores
    path('applied-certificates/delete/<int:pk>/', admin_view.DeleteAppliedCertificateView.as_view(), name='delete-applied-certificate'),
]
