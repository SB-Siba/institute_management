# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.views import View
# from django.contrib import messages
# from django.utils.decorators import method_decorator
# from helpers import utils, api_permission
# from django.forms.models import model_to_dict
# import json
# from helpers import utils
# from app_common import models as common_model
# from app_common.checkout.serializer import OrderSerializer
# from .forms import OrderUpdateForm
# from ..tasks import update_order_status
# import logging

# app = "orders/admin/"

# # ================================================== patient management ==========================================

# @method_decorator(utils.super_admin_only, name='dispatch')
# class OrderList(View):
#     model = common_model.Order
#     template = app + "order_list.html"

#     def get(self,request):

#         order_list = self.model.objects.all().order_by('-id')
#         paginated_data = utils.paginate(request, order_list, 50)
#         order_status_options = common_model.Order.ORDER_STATUS
      
#         context = {
#             "order_list":paginated_data,
#             "order_status_options":order_status_options,
#         }
#         return render(request, self.template,context)

# @method_decorator(utils.super_admin_only, name='dispatch')
# class OrderStatusSearch(View):
#     model = common_model.Order
#     template = app + "order_list.html"

#     def get(self,request):
#         filter_by = request.GET.get('filter_by')
#         order_list = self.model.objects.filter(order_status = filter_by)
#         paginated_data = utils.paginate(request, order_list, 50)
#         order_status_options = common_model.Order.ORDER_STATUS
        
#         context = {
#             "order_list":paginated_data,
#             "order_status_options":order_status_options,
#         }
#         return render(request, self.template,context)


# @method_decorator(utils.super_admin_only, name='dispatch')
# class OrderSearch(View):
#     model = common_model.Order
#     template = app + "order_list.html"

#     def get(self,request):
#         query = request.GET.get('query')
#         order_list = self.model.objects.filter(uid__icontains = query)
#         order_status_options = common_model.Order.ORDER_STATUS

#         context = {
#             "order_list":order_list,
#             "order_status_options":order_status_options,
#         }
#         return render(request, self.template,context)


# @method_decorator(utils.super_admin_only, name='dispatch')
# class OrderDetail(View):
#     model = common_model.Order
#     form_class = OrderUpdateForm
#     template= app + "order_detail.html"

#     def get(self,request, order_uid):
#         # order_o = common_model.Cart.objects.all().delete()
#         order = common_model.Order.objects.get(uid = order_uid)
#         form = OrderUpdateForm(instance=order, initial={'order_status': order.order_status})
#         product_list = []
#         variant_or_not = []
#         product_quantity = []
#         size = []
#         color = []
#         total_quantity= 0
#         grand_total = 0
#         try:
#             grand_total = order.order_meta_data['final_cart_value']
#         except Exception:
#             grand_total = order.order_meta_data['final_value']
#         order_address = order.address
#         for i,j in order.products.items():
#             p_obj = common_model.Products.objects.get(name=j['info']['name'])
#             if p_obj.variant != "None":
#                 v_obj = common_model.Variants.objects.get(product__name = j['info']['name'],color__name = j['info']['color'],size__code = j['info']['size'])
#                 product_list.append(v_obj)
#                 variant_or_not.append("Yes")
#             else:
#                 product_list.append(p_obj)
#                 variant_or_not.append("No")
#             product_quantity.append(j['quantity'])
#             size.append(j['info']['size'])
#             color.append(j['info']['color'])
#             total_quantity+= int(j['quantity'])
#         zipproduct = zip(product_list, product_quantity,size,color,variant_or_not)

#         context={
#             'order':order,
#             'grand_total':grand_total,
#             'zipproduct':zipproduct,
#             'total_quantity':total_quantity,
#             "MEDIA_URL":settings.MEDIA_URL,
#             "form": form,
#             "order_address":order_address
#         }
#         return render(request, self.template, context)
    
#     def post(self,request, order_uid):
#         order = self.model.objects.get(uid = order_uid)

#         form = self.form_class(request.POST, instance = order)

#         if form.is_valid():
#             obj=form.save()
#             # update_order_status.delay(obj.user.email, OrderSerializer(obj).data)
#             messages.success(request, 'Order Status is updated....')

#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f'{field}: {error}')

#         return redirect('admin_dashboard:order_detail', order_uid = order_uid)


# @method_decorator(utils.super_admin_only, name='dispatch')
# class DownloadInvoice(View):
#     model = common_model.Order
#     form_class = OrderUpdateForm
#     template= 'app_common/checkout/invoice.html'

#     def get(self,request, order_uid):
#         order = self.model.objects.get(uid = order_uid)
#         data = OrderSerializer(order).data
#         products = []
#         quantities = []
#         price_per_unit = []
#         total_prices = []
#         for product,p_overview in data['order_meta_data']['products'].items():
#             products.append(product)
#             quantities.append(p_overview['quantity'])
#             price_per_unit.append(p_overview['price_per_unit'])
#             total_prices.append(p_overview['total_price'])
#             # product['product']['quantity']=product['quantity']
#         prod_quant = zip(products, quantities,price_per_unit,total_prices)
#         try:
#             final_total = data['order_meta_data']['final_cart_value']
#         except Exception:
#             final_total = data['order_meta_data']['final_value']
#         context ={
#             'order':data,
#             'address':data['address'],
#             'user':order.user,
#             'productandquantity':prod_quant,
#             'GST':data['order_meta_data']['charges']['GST'],
#             'delevery_charge':data['order_meta_data']['charges']['Delivery'],
#             'gross_amt':data['order_meta_data']['our_price'],
#             'discount':data['order_meta_data']['coupon_validation_result']['discount'],
#             'final_total':final_total
#         }

#         return render(request, self.template, context)
        