from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Give your title",
        default_version='v1',
        description="service",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    
    
    path("", include("users.urls.urls")),
    path("", include("users.urls.api_urls")),

    path("niwa_agro", include("app_common.urls.urls")),
    path("product", include("product.urls.urls")),
    path("cart", include("cart.urls.urls")),
    path("orders", include("orders.urls.urls")), 
    path("payment", include("payment.urls.urls")), 



    path(
        "swagger/download/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "swagger/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)