from django.urls import path
from orders.orders_views import admin_orders_views,user_orders_views

app_name = 'orders'




urlpatterns = [
    path('place-order/', user_orders_views.PlaceOrder.as_view(), name='place_order'),
    path('your/oders/',user_orders_views.UserOrder.as_view(),name='orders'),
    path('order/order_detail/<str:order_uid>', user_orders_views.OrderDetail.as_view(), name='order_detail'),
    path('delete_all_data/', user_orders_views.DeleteAllDataView.as_view(), name='delete_all_data'),

]