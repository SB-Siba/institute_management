from django.urls import path
from payment.payment_views import user_payment_views

app_name = 'payment'




urlpatterns = [
    path('paymentsuccess/',user_payment_views.PaymentSuccess.as_view(),name='paymentsuccess'),
    
]