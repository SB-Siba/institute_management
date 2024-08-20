from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from orders.serializer import OrderSerializer
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


class UserDownloadInvoice(View):
    model = Order
    template = 'orders/admin/invoice.html'

    def get(self, request, order_uid):
        order = self.model.objects.get(uid=order_uid)
        data = OrderSerializer(order).data
        
        products = []
        quantities = []
        price_per_unit = []
        total_prices = []

        total_cgst = 0.0
        total_sgst = 0.0

        # Loop through each product to extract and calculate required information
        for product_id, p_overview in data['order_meta_data']['products'].items():
            products.append(p_overview['name'])
            quantities.append(p_overview['quantity'])
            price_per_unit.append(p_overview['product_discount_price'])
            total_prices.append(p_overview['total_price'])

            # Calculate the total CGST and SGST
            total_cgst += float(p_overview.get('cgst_amount', 0))
            total_sgst += float(p_overview.get('sgst_amount', 0))

        prod_quant = zip(products, quantities, price_per_unit, total_prices)

        try:
            final_total = data['order_meta_data']['final_cart_value']
        except KeyError:
            final_total = data['order_meta_data']['final_value']

        # Prepare context data for rendering the invoice
        context = {
            'order': data,
            'address': data['address'],
            'user': order.user,
            'productandquantity': prod_quant,
            'delivery_charge': data['order_meta_data']['charges']['Delivery'],
            'cgst_amount': total_cgst,
            'sgst_amount': total_sgst,
            'gross_amt': data['order_meta_data']['our_price'],
            'discount': data['order_meta_data'].get('discount_amount', 0),
            'final_total': final_total
        }

        # Render the template with the provided context
        return render(request, self.template, context)