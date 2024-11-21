from django.urls import path
from certificate.certificate_view import admin_view

app_name = 'certificate'

urlpatterns = [
    path('exam-results/', admin_view.AllExamResultsView.as_view(), name='exam_results'),
    path('designed-certificate/', admin_view.DesignedCertificateView.as_view(), name='designed_certificate'),
    path('requested-certificates/', admin_view.RequestedCertificatesListView.as_view(), name='requested_certificates'),
    path('apply-certificate/', admin_view.ApplyCertificateView.as_view(), name='apply_certificate'),
    path('approved-certificates/', admin_view.ApprovedCertificatesListView.as_view(), name='approved_certificates'),
    path('delete-certificate-application/<int:pk>/', admin_view.DeleteCertificateApplicationView.as_view(), name='delete-certificate-application'),
    path('applied-certificates/delete/<int:pk>/', admin_view.DeleteAppliedCertificateView.as_view(), name='delete-applied-certificate'),
    path('toggle-certificate-status/<int:pk>/', admin_view.toggle_certificate_status, name='toggle-certificate-status'),
    path('update/<int:pk>/', admin_view.UpdateCertificateView.as_view(), name='update-certificate'),
]
