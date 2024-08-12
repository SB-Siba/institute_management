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
    template = app + "order_details.html"

    def get(self, request, order_uid):
        order = Order.objects.get(uid=order_uid)

        product_list = []
        product_quantity = []
        total_quantity = 0
        grand_total = 0

        try:
            grand_total = order.order_meta_data['final_cart_value']
        except Exception:
            grand_total = order.order_meta_data['final_value']

        for i, j in order.products.items():
            p_obj = Products.objects.get(name=j['info']['name'])
            product_list.append(p_obj)
            product_quantity.append(j['quantity'])
            total_quantity += int(j['quantity'])

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
