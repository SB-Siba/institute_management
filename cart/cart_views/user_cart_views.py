from django.shortcuts import get_object_or_404, redirect,render
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from product.models import Products, SimpleProduct, Category
from orders.models import Order
from cart.models import Cart
from cart.serializer import CartSerializer,DirectBuySerializer
from decimal import Decimal, InvalidOperation,ROUND_HALF_UP
from uuid import uuid4
from payment import razorpay

class ShowCart(View):
    def get(self, request):
        category_obj = Category.objects.all()
        user = request.user

        if user.is_authenticated:
            cartItems = Cart.objects.filter(user=user).first()
            if not cartItems or not cartItems.products:
                products = {}
            else:
                products = cartItems.products or {}
        else:
            cartItems = None
            products = request.session.get('cart', {}).get('products', {})

        totaloriginalprice = Decimal('0.00')
        totalPrice = Decimal('0.00')
        GST = Decimal('0.00')
        Delivery = Decimal('0.00')
        final_cart_value = Decimal('0.00')
        free_delivery_threshold = Decimal('0.00')

        for product_key, product_info in products.items():
            product_key_parts = product_key.split('_')
            product_id = product_key_parts[0]

            # Retrieve the SimpleProduct instance
            simple_product = SimpleProduct.objects.get(id=product_id)

            max_price = Decimal(simple_product.product_max_price)
            discount_price = Decimal(simple_product.product_discount_price)
            quantity = product_info.get('quantity', 0)

            # Calculate the GST for each product
            gst_rate = simple_product.sgst_rate + simple_product.cgst_rate
            gst_for_product = (discount_price * gst_rate) * quantity
            GST += gst_for_product

            # Calculate total prices
            totaloriginalprice += max_price * quantity
            totalPrice += discount_price * quantity

            # Set Delivery charge and free delivery threshold
            Delivery = simple_product.delivery_charge_per_bag
            free_delivery_threshold = simple_product.delivery_free_order_amount

        # Calculate discount price
        discount_price = totaloriginalprice - totalPrice

        # Calculate final cart value
        final_cart_value = totalPrice + GST

        # Apply delivery charges if applicable
        if final_cart_value < free_delivery_threshold:
            final_cart_value += Delivery

        if user.is_authenticated and cartItems:
            cartItems.total_price = float(totalPrice)
            cartItems.save()

        context = {
            'category_obj': category_obj,
            'cartItems': cartItems,
            'products': products,
            'totaloriginalprice': float(totaloriginalprice),
            'totalPrice': float(totalPrice),
            'GST': float(GST),
            'Delivery': float(Delivery),
            'final_cart_value': float(final_cart_value),
            'discount_price': float(discount_price),
            'MEDIA_URL': settings.MEDIA_URL,
        }

        return render(request, "cart/user/cartpage.html", context)



class AddToCartView(View):
    def get(self, request, product_id):
        try:
            # Check if the user is authenticated
            if request.user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=request.user)
                is_user_authenticated = True
            else:
                cart = request.session.get('cart', {'products': {}})
                is_user_authenticated = False

            # Get the product
            product_obj = get_object_or_404(SimpleProduct, id=product_id)
            product_key = str(product_obj.id)

            # Prepare product info
            product_info = {
                'quantity': 1,
                'total_price': float(product_obj.product_discount_price),
            }

            # Retrieve existing products from the cart
            products = cart.products if is_user_authenticated else cart.get('products', {})
            
            if product_key in products:
                # If the product is already in the cart, increase quantity and update total price
                products[product_key]['quantity'] += 1
                products[product_key]['total_price'] = float(products[product_key]['quantity'] * product_obj.product_discount_price)
            else:
                # Add new product to the cart
                products[product_key] = product_info

            # Save the cart
            if is_user_authenticated:
                cart.products = products
                cart.save()
            else:
                cart['products'] = products
                request.session['cart'] = cart
                request.session.modified = True

            messages.success(request, f"{product_obj.product.name} added to cart.")
            return redirect("users:home")
        except Exception as e:
            print(f"Add to cart error: {e}")
            return HttpResponse(f"An error occurred: {e}", status=500)

class ManageCart(View):
    def get(self, request, c_p_uid):
        operation_type = request.GET.get('operation')

        # Determine the cart based on user authentication
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            products = cart.products or {}
        else:
            cart = request.session.get('cart', {'products': {}})
            products = cart.get('products', {})

        # Initialize variables
        product_found = False

        for product_key, product_info in products.items():
            # Match the product based on UID
            product_id = product_key.split('_')[0]
            simple_product = SimpleProduct.objects.get(id=product_id)
            uid = simple_product.product.uid or f"{simple_product.product.name}_{simple_product.id}"

            if c_p_uid == uid:
                product_found = True
                if operation_type == 'plus':
                    # Increase quantity and total price
                    product_info['quantity'] += 1
                    product_info['total_price'] = float(product_info['quantity'] * simple_product.product_discount_price)
                elif operation_type == 'min':
                    if product_info['quantity'] > 1:
                        # Decrease quantity and total price
                        product_info['quantity'] -= 1
                        product_info['total_price'] = float(product_info['quantity'] * simple_product.product_discount_price)
                    else:
                        # Remove the product if quantity becomes zero
                        products.pop(product_key)
                break

        if not product_found:
            return HttpResponse(f"Product with UID {c_p_uid} not found in cart.", status=404)

        # Save the updated cart
        if request.user.is_authenticated:
            cart.products = products
            cart.save()
        else:
            cart['products'] = products
            request.session['cart'] = cart
            request.session.modified = True

        return redirect('cart:showcart')



def RemoveFromCart(request, cp_uid):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        if cp_uid in cart.products:
            cart.products.pop(cp_uid)
            cart.save()
    else:
        cart = request.session.get('cart', {'products': {}})
        products = cart.get('products', {})
        if cp_uid in products:
            products.pop(cp_uid)
            cart['products'] = products
            request.session['cart'] = cart
            request.session.modified = True

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
                    if key in user_cart_products:
                        user_cart_products[key]['quantity'] += value['quantity']
                    else:
                        user_cart_products[key] = value

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

        discount_price = totaloriginalprice - totalPrice
        addresses = user.address or []

        # Razorpay order creation
        status, rz_order_id = razorpay.create_order_in_razPay(
            amount=int(final_cart_value * 100)  # Amount in paise
        )

        context = {
            "cart": cart.products,
            "rz_order_id": rz_order_id,
            "api_key": settings.RAZORPAY_API_KEY,
            "addresses": addresses,
            'totaloriginalprice': totaloriginalprice,
            'totalPrice': totalPrice,
            'GST': GST,
            'Delivery': Delivery,
            'final_cart_value': final_cart_value,
            'discount_price': discount_price,
            "MEDIA_URL": settings.MEDIA_URL,
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
        url = reverse('cart:directbuycheckout', args=[p_id])

        return HttpResponseRedirect(url)






# checkout address

class AddAddress(View):
    def post(self, request):
        if request.method == 'POST':
            landmark1 = request.POST["landmark1"]
            landmark2 = request.POST["landmark2"]
            country = request.POST["country"]
            state = request.POST["state"]
            city = request.POST["city"]
            mobile_no = request.POST["mobile_no"]
            zipcode = request.POST["zipcode"]

            address_id = str(uuid4())

            address_data = {
                "id": address_id,
                "landmark1": landmark1,
                "landmark2": landmark2,
                "country": country,
                "state": state,
                "city": city,
                "mobile_no": mobile_no,
                "zipcode": zipcode,
            }
            user = request.user
            addresses = user.address or []
            addresses.append(address_data)
            user.address = addresses
            user.save()

            return redirect('cart:checkout')
        else:
            return redirect('app_coomo:home')




def update_address_view(request):
    if request.method == 'POST':
        user = request.user
        user_obj = get_object_or_404(User, id=user.id)
        a_id = request.POST.get('a_id')
        landmark1 = request.POST.get('landmark1')
        landmark2 = request.POST.get('landmark2')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        mobile_no = request.POST.get('mobile_no')
        zipcode = request.POST.get('zipcode')

        addresses = user_obj.address or []

        try:
            # Find and update the address with the specified id
            for address in addresses:
                if address['id'] == a_id:
                    address.update({
                        'landmark1': landmark1,
                        'landmark2': landmark2,
                        'country': country,
                        'state': state,
                        'city': city,
                        'mobile_no': mobile_no,
                        'zipcode': zipcode,
                    })
                    break

            # Save the updated addresses back to the user model
            user_obj.address = addresses
            user_obj.save()
            messages.success(request, 'Address updated successfully.')

            # Redirect to the checkout page
            return redirect('cart:checkout')

        except Exception as e:
            messages.error(request, f'Failed to update address: {str(e)}')
            return redirect('app_commo:home')
    else:
        return redirect('app_common:home')




class DeleteAddress(View):
    def get(self, request, address_id):
        user = request.user
        addresses = user.address or []

        # Remove the address with the specified ID
        addresses = [address for address in addresses if address.get('id') != address_id]

        # Save the updated list of addresses back to the user model
        user.address = addresses
        user.save()

        # Redirect to the checkout page
        return redirect('cart:checkout')