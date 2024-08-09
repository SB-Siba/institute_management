from django.shortcuts import get_object_or_404, redirect,render
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from product.models import Products, SimpleProduct, Category
from orders.models import Order
from cart.models import Cart
from cart.serializer import CartSerializer,DirectBuySerializer
from decimal import Decimal

class ShowCart(View):
    def get(self, request):
        category_obj = Category.objects.all()
        user = request.user
        
        if user.is_authenticated:
            try:
                cart = get_object_or_404(Cart, user=user)
                cart_data = CartSerializer(cart).data
                
                context = {
                    'category_obj': category_obj,
                    'cartItems': cart,
                    'products': cart_data['products_data']['products'],
                    'totaloriginalprice': float(cart_data['products_data']['gross_cart_value']),
                    'totalPrice': float(cart_data['products_data']['our_price']),
                    'GST': float(cart_data['products_data']['charges']['GST']),
                    'Delivery': float(cart_data['products_data']['charges']['Delivery']),
                    'final_cart_value': float(cart_data['products_data']['final_cart_value']),
                    'discount_price': float(cart_data['products_data']['discount_amount']),
                    'MEDIA_URL': settings.MEDIA_URL,
                }
            except Exception as e:
                print('Error:', str(e))
                context = {
                    'category_obj': category_obj,
                    'cartItems': None,
                    'products': {},
                    'totaloriginalprice': 0,
                    'totalPrice': 0,
                    'GST': 0,
                    'Delivery': 0,
                    'final_cart_value': 0,
                    'discount_price': 0,
                    'MEDIA_URL': settings.MEDIA_URL,
                }
        else:
            cart = request.session.get('cart', {})
            cart_data = CartSerializer(data={'products': cart}).data if cart else {}
            
            context = {
                'category_obj': category_obj,
                'cartItems': None,
                'products': cart_data.get('products_data', {}).get('products', {}),
                'totaloriginalprice': float(cart_data.get('products_data', {}).get('gross_cart_value', 0)),
                'totalPrice': float(cart_data.get('products_data', {}).get('our_price', 0)),
                'GST': float(cart_data.get('products_data', {}).get('charges', {}).get('GST', 0)),
                'Delivery': float(cart_data.get('products_data', {}).get('charges', {}).get('Delivery', 0)),
                'final_cart_value': float(cart_data.get('products_data', {}).get('final_cart_value', 0)),
                'discount_price': float(cart_data.get('products_data', {}).get('discount_amount', 0)),
                'MEDIA_URL': settings.MEDIA_URL,
            }

        return render(request, "cart/user/cartpage.html", context)



class AddToCartView(View):
    def get(self, request, product_id):
        try:
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                is_user_authenticated = True
            else:
                cart = request.session.get('cart', {})
                is_user_authenticated = False

            product_obj = get_object_or_404(SimpleProduct, id=product_id)
            product_images = product_obj.product.image
            image_url = product_images.url if product_images else None

            product_uid = product_obj.product.pk or f"{product_obj.product.name}_{product_obj.id}"
            product_info = {
                'product_id': product_obj.id,
                'uid': product_uid,
                'name': product_obj.product.name,
                'image': image_url,
                'max_price': product_obj.product_max_price,
                'discount_price': product_obj.product_discount_price,
            }
            product_key = str(product_obj.id)

            if is_user_authenticated:
                products = cart.products or {}
            else:
                products = cart or {}

            if product_key in products:
                products[product_key]['quantity'] += 1
                products[product_key]['total_price'] += product_obj.product_discount_price
            else:
                products[product_key] = {
                    'info': product_info,
                    'quantity': 1,
                    'total_price': product_obj.product_discount_price
                }

            if is_user_authenticated:
                cart.products = products
                cart.total_price = sum(item['total_price'] for item in products.values())
                cart.save()
            else:
                cart['products'] = products
                cart['total_price'] = sum(item['total_price'] for item in products.values())
                request.session['cart'] = cart
                request.session.modified = True

            messages.success(request, f"{product_obj.product.name} added to cart.")
            return redirect("users:home")
        except Exception as e:
            print(e)
            return HttpResponse(f"An error occurred: {e}", status=500)


class ManageCart(View):
    def get(self, request, c_p_uid):
        operation_type = request.GET.get('operation')

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            old_product_dict = cart.products
        else:
            cart = request.session.get('cart', {})
            old_product_dict = cart

        # Assuming `c_p_uid` is a string, and `j['info']['uid']` is also a string
        if c_p_uid:
            for i, j in old_product_dict.items():
                if c_p_uid == j['info']['uid']:  # Ensure comparison is between strings
                    if operation_type == 'plus':
                        j['quantity'] += 1
                    elif operation_type == 'min':
                        if j['quantity'] > 1:
                            j['quantity'] -= 1    
                        else:
                            old_product_dict.pop(i)
                            break

        if request.user.is_authenticated:
            cart.products = old_product_dict
            cart.save()
        else:
            request.session['cart'] = old_product_dict
            request.session.modified = True

        return redirect('cart:showcart')




def RemoveFromCart(request, cp_uid):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        for i, j in cart.products.items():
            if cp_uid == j['info']['uid']:
                cart.products.pop(i)
                cart.save()
                break
    else:
        cart = request.session.get('cart', {})
        for i, j in cart.items():
            if cp_uid == j['info']['uid']:
                cart.pop(i)
                request.session['cart'] = cart
                request.session.modified = True
                break

    return redirect("cart:showcart")




@method_decorator(login_required(login_url='users:login'), name='dispatch')
class Checkout(View):
    template = "cart/user/checkout.html"
    model = Order

    def get(self, request):
        user = request.user

        try:
            # Merge session cart with user cart if available
            session_cart = request.session.get('cart', {})
            if session_cart:
                user_cart, created = Cart.objects.get_or_create(user=user)
                user_cart_products = user_cart.products or {}

                for key, value in session_cart.get('products', {}).items():
                    quantity = value.get('quantity', 1)
                    if key in user_cart_products:
                        user_cart_products[key]['quantity'] += quantity
                    else:
                        user_cart_products[key] = value
                        user_cart_products[key]['quantity'] = quantity

                user_cart.products = user_cart_products
                user_cart.save()
                del request.session['cart']  # Clear session cart after merging

            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return redirect("cart:showcart")

        order_details = CartSerializer(cart).data
        totaloriginalprice = Decimal(order_details['products_data']['gross_cart_value'])
        totalPrice = Decimal(order_details['products_data']['our_price'])
        GST = Decimal(order_details['products_data']['charges']['GST'])
        Delivery = Decimal(order_details['products_data']['charges']['Delivery'])
        final_cart_value = Decimal(order_details['products_data']['final_cart_value'])
        addresses = user.address or []

        # Razorpay integration is commented out for now
        # status, rz_order_id = rozerpay.create_order_in_razPay(
        #     amount=int(float(final_cart_value) * 100)  # Amount in paise
        # )

        discount_price = totaloriginalprice - totalPrice

        context = {
            "cart": cart.products,
            # "rz_order_id": rz_order_id,  # Uncomment when adding Razorpay integration
            # "api_key": settings.RAZORPAY_API_KEY,  # Uncomment when adding Razorpay integration
            "addresses": addresses,
            'totaloriginalprice': totaloriginalprice,
            'totalPrice': totalPrice,
            'GST': GST,
            'Delivery': Delivery,
            'final_cart_value': final_cart_value,
            'discount_price': discount_price,
            "MEDIA_URL": settings.MEDIA_URL
        }

        return render(request, self.template, context)



@method_decorator(login_required(login_url='shoppingsite:login'), name='dispatch')
class DirectBuyCheckout(View):
    template = "cart/user/directbuycheckout.html"  # Update with your actual template path

    def get(self, request, p_id):
        user = request.user
        product = get_object_or_404(Products, id=p_id)
        product_uid = product.uid

        our_price = 0
        totaloriginalprice = 0
        GST = 0
        Delivery = 0
        final_value = 0
        discount_amount = 0

        order_details = DirectBuySerializer(product).data
        
        for i, j in order_details.items():
            totaloriginalprice = Decimal(j['gross_value'])
            our_price = Decimal(j['our_price'])
            GST = Decimal(j['charges']['GST'])
            Delivery = Decimal(j['charges']['Delivery'])
            final_value = j['final_value']
            discount_amount = j['discount_amount']

        addresses = user.address or []
        # Commented out Razorpay fields for now
        # status, rz_order_id = rozerpay.create_order_in_razPay(amount=int(float(final_value)))

        context = {
            'p_id': p_id,
            'our_price': our_price,
            'totaloriginalprice': totaloriginalprice,
            "total_price": final_value,
            'GST': GST,
            'Delivery': Delivery,
            'discount_amount': discount_amount,
            "MEDIA_URL": settings.MEDIA_URL,
            # "rz_order_id": rz_order_id,
            # "api_key": settings.RAZORPAY_API_KEY,
            "product_uid": product_uid,
            "addresses": addresses,
        }

        return render(request, self.template, context)

    def post(self, request):
        p_id = request.POST['product_id']
        url = reverse('shoppingsite:directbuycheckout', args=[p_id])

        return HttpResponseRedirect(url)
