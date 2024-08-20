from django.views import View
from django.shortcuts import redirect, get_object_or_404,render
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from cart.models import Cart
from orders.models import Order
from users.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from cart.serializer import CartSerializer
from payment import razorpay  # Assuming you have a utility function for Razorpay verification
import json

from users.user_views.emails import send_template_email

app = 'payment/'

@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccess(View):

    model = Order

    def post(self, request):
        user = request.user
        cart = Cart.objects.get(user=request.user)
        data = json.loads(request.body)
        address_id = data.get('address_id')
        order_details = CartSerializer(cart).data

        try:
            ord_meta_data = {}
            for i, j in order_details.items():
                ord_meta_data.update(j)
            print(ord_meta_data)
            t_price = float(ord_meta_data['final_cart_value'])

            user_addresses = user.address
            selected_address = None
            for address in user_addresses:
                if address['id'] == address_id:
                    selected_address = address
                    break

            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            print(razorpay_order_id, razorpay_payment_id, razorpay_signature)

            if razorpay.verify_signature(data):
                try:
                    order = self.model(
                        user=user,
                        full_name=cart.user.full_name,
                        email=cart.user.email,
                        products=cart.products,
                        order_value=t_price,
                        address=selected_address,
                        order_meta_data=ord_meta_data,
                        razorpay_payment_id=razorpay_payment_id,
                        razorpay_order_id=razorpay_order_id,
                        razorpay_signature=razorpay_signature,
                    )
                    # Send confirmation email
                    context = {
                        'full_name': user.full_name,
                        'email': user.email,
                        'order_value': t_price,
                        'order_details': ord_meta_data,
                        'address': selected_address,
                    }
                    send_template_email(
                        subject='Order Confirmation',
                        template_name='users/email/order_confirmation.html',
                        context=context,
                        recipient_list=[user.email]
                    )
                    order.save()
                    messages.success(request, "Order Successful!")
                    cart.delete()
                    return redirect("users:home")
                except Exception as e:
                    print(f"Error while placing order: {e}")
                    messages.error(request, "Error while placing Order.")
                    return redirect("cart:checkout")
            else:
                print('Payment is not verified')
                messages.error(request, "Payment verification failed.")
                return redirect("cart:checkout")
        except Exception as e:
            print(f"Exception caught: {e}")
            messages.error(request, "An error occurred.")
            return redirect("cart:checkout")



class SuccessPage(View):
    template = app + "payment_success.html"
    def get(self, request):
        return render(request, self.template)