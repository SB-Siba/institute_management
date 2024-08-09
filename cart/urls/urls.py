from django.urls import path
from product import views
from django.conf import settings
from cart.cart_views import user_cart_views
from django.conf.urls.static import static


app_name = 'cart'

urlpatterns = [
    path('show-cart/', user_cart_views.ShowCart.as_view(), name='showcart'),
    path('add-to-cart/<int:product_id>/', user_cart_views.AddToCartView.as_view(), name='addtocart'),
    path('manage-cart/<int:c_p_uid>/', user_cart_views.ManageCart.as_view(), name='managecart'),
    path('remove-from-cart/<str:cp_uid>/', user_cart_views.RemoveFromCart, name='removefromcart'),
    path('checkout/',user_cart_views.Checkout.as_view(),name='checkout'),
    path('directbuychecout/<int:p_id>',user_cart_views.DirectBuyCheckout.as_view(),name='directbuycheckout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)