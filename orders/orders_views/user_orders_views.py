from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from django.views import View
from orders.models import Order
from product.models import Products
app = "orders/user/"
class UserOrder(View):
    template = app + "user_order.html"

    def get(self, request):
        
        user = request.user
        
        orders = Order.objects.filter(user=user).order_by("-id")
        return render(request, self.template, {'orders':orders})


class OrderDetail(View):
    template = app + 'order_details.html'  # Update 'app' with the correct path

    def get(self, request, order_uid):
        # Fetch the order using the UID
        order = get_object_or_404(Order, uid=order_uid)
        
        product_list = []
        product_quantity = []
        total_quantity = 0
        grand_total = 0

        # Extract the grand total from the order's metadata
        try:
            grand_total = order.order_meta_data.get('final_cart_value', 0)
        except KeyError:
            grand_total = order.order_meta_data.get('final_value', 0)

        # Iterate over the products in the order
        for product_id, details in order.products.items():
            product = get_object_or_404(Products, name=details['info']['name'])
            product_list.append(product)
            product_quantity.append(details['quantity'])
            total_quantity += int(details['quantity'])

        # Zip together the products and their quantities
        zipproduct = zip(product_list, product_quantity)

        context = {
            'order': order,
            'grand_total': grand_total,
            'zipproduct': zipproduct,
            'total_quantity': total_quantity,
            "MEDIA_URL": settings.MEDIA_URL
        }
        return render(request, self.template, context)


class DeleteAllDataView(View):
    def get(self, request):
        try:      
            Products.objects.all().delete()
            Order.objects.all().delete()

            message = "All data deleted successfully."
            status_code = 200
        except Exception as e:
            message = f"Failed to delete data: {str(e)}"
            status_code = 500
        return HttpResponse(message, status=status_code)
