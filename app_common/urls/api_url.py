from django.urls import path
from app_common.app_common_views import api_views_app_common

urlpatterns = [ 
    path('privacy_policy_api', api_views_app_common.ApiPrivacyPolicy.as_view(),),
    path('terms_and_conditions', api_views_app_common.ApiTermsCondition.as_view(),),
    path('about_us', api_views_app_common.ApiAboutUs.as_view(),),
    path('return_policy', api_views_app_common.ApiReturnPolicy.as_view(),),

]