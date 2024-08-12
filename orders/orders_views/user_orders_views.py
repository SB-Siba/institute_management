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

class PlaceOrder(View):
    def post(self, request, *args, **kwargs):
        # Assuming order creation logic is here
        order = Order.objects.create(
            user=request.user,
            products=request.session.get('cart_products', {}),
            order_meta_data={'final_cart_value': request.session.get('final_cart_value', 0)}
        )
        # Save the order and clear the session cart
        order.save()
        request.session.pop('cart_products', None)
        request.session.pop('final_cart_value', None)
        
        # Redirect to the OrderDetail page
        return redirect(reverse('orders:order_detail', kwargs={'order_uid': order.uid}))

class OrderDetail(View):
    template = app + 'order_details.html'  # Update 'app' with the correct path

    def get(self, request, order_uid):
        order = get_object_or_404(Order, uid=order_uid)

        product_list = []
        product_quantity = []
        total_quantity = 0
        grand_total = 0

        try:
            grand_total = order.order_meta_data['final_cart_value']
        except KeyError:
            grand_total = order.order_meta_data.get('final_value', 0)  # Provide a default value if needed

        # Debugging: Check the content of `order.products`
        print(order.products)

        for product_info in order.products.values():
            try:
                p_obj = Products.objects.get(name=product_info['info']['name'])
                product_list.append(p_obj)
                product_quantity.append(product_info['quantity'])
                total_quantity += int(product_info['quantity'])
            except Products.DoesNotExist:
                print(f"Product with name '{product_info['info']['name']}' does not exist.")

        zipproduct = zip(product_list, product_quantity)

        context = {
            'order': order,
            'grand_total': grand_total,
            'zipproduct': zipproduct,
            'total_quantity': total_quantity,
            "MEDIA_URL": settings.MEDIA_URL,
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
