from rest_framework import serializers
from .models import Cart
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from product.models import Products,SimpleProduct,ImageGallery

class CartSerializer(serializers.ModelSerializer):
    products_data = serializers.SerializerMethodField()

    def get_products_data(self, obj):
        total_cart_items = 0
        gross_cart_value = Decimal('0')
        our_price = Decimal('0')
        charges = {}
        products = {}

        for key, value in obj.products.items():
            product_key_parts = key.split('_')
            product_id = product_key_parts[0]
            try:
                simple_product = get_object_or_404(SimpleProduct, id=product_id)
                product = simple_product.product
                quantity = int(value['quantity'])

                gross_cart_value += Decimal(simple_product.product_max_price) * quantity
                our_price += Decimal(simple_product.product_discount_price) * quantity
                total_cart_items += quantity

                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'image': product.image.url if product.image else None,
                    'product_max_price': str(simple_product.product_max_price),
                    'product_discount_price': str(simple_product.product_discount_price),
                    'discount_percentage': simple_product.discount_percentage(),
                    'quantity': quantity,
                    'total_price': str(Decimal(simple_product.product_discount_price) * quantity),
                    'images': simple_product.image_gallery.first().images if simple_product.image_gallery.exists() else [],
                    'video': simple_product.image_gallery.first().video if simple_product.image_gallery.exists() else [],
                }

                products[key] = product_data

            except Exception as e:
                print(e)

        discount_amount = gross_cart_value - our_price
        final_cart_value = our_price

        if settings.GST_CHARGE > 0:
            gst_value = final_cart_value * Decimal(str(settings.GST_CHARGE))
            charges['GST'] = gst_value.quantize(Decimal('0.01'))
        else:
            charges['GST'] = Decimal('0')
        if final_cart_value < settings.DELIVARY_FREE_ORDER_AMOUNT:
            delivery_charge = Decimal(str(settings.DELIVARY_CHARGE_PER_BAG))
            charges['Delivery'] = delivery_charge.quantize(Decimal('0.01'))
        else:
            charges['Delivery'] = Decimal('0')

        for key, value in charges.items():
            final_cart_value += value

        result = {
            'products': products,
            'total_cart_items': total_cart_items,
            'gross_cart_value': "{:.2f}".format(float(gross_cart_value.quantize(Decimal('0.01')))),
            'our_price': "{:.2f}".format(float(our_price.quantize(Decimal('0.01')))),
            'discount_amount': "{:.2f}".format(float(discount_amount.quantize(Decimal('0.01')))),
            'discount_percentage': "{:.1f}".format(float((discount_amount / gross_cart_value) * 100)) if gross_cart_value > 0 else "0.0",
            'charges': {k: "{:.2f}".format(float(v.quantize(Decimal('0.01')))) for k, v in charges.items()},
            'final_cart_value': "{:.2f}".format(float(final_cart_value.quantize(Decimal('0.01')))),
        }

        return result

    class Meta:
        model = Cart
        fields = ["products_data"]




class DirectBuySerializer(serializers.ModelSerializer):
    products_data = serializers.SerializerMethodField()

    def get_products_data(self, obj):
        total_items = 1
        gross_value = Decimal('0')
        our_price = Decimal('0')
        charges = {}

        products = {}

        try:
            product = get_object_or_404(Products, id=obj.id)
            simple_product = get_object_or_404(SimpleProduct, product=product)
            image_gallery = ImageGallery.objects.filter(simple_product=simple_product).first()

            gross_value += Decimal(simple_product.product_max_price)
            our_price += Decimal(simple_product.product_discount_price)

            products[product.name] = {
                'quantity': 1,
                'price_per_unit': "{:.2f}".format(float(simple_product.product_discount_price)),
                'total_price': "{:.2f}".format(float(Decimal(simple_product.product_discount_price).quantize(Decimal('0.01')))),
                'images': image_gallery.images if image_gallery else [],
                'video': image_gallery.video if image_gallery else []
            }
        except Exception as e:
            print(f"Error retrieving product: {e}")
            charges['GST'] = Decimal('0')
            charges['Delivery'] = Decimal('0')

        discount_amount = gross_value - our_price
        final_value = our_price

        gst_charge = Decimal(getattr(settings, 'GST_CHARGE', '0.00'))
        delivery_charge = Decimal(getattr(settings, 'DELIVERY_CHARGE_PER_BAG', '0.00'))
        delivery_free_order_amount = Decimal(getattr(settings, 'DELIVERY_FREE_ORDER_AMOUNT', '0.00'))

        if gst_charge > 0:
            gst_value = final_value * gst_charge / 100
            charges['GST'] = gst_value.quantize(Decimal('0.01'))
        else:
            charges['GST'] = Decimal('0')

        if final_value < delivery_free_order_amount:
            delivery_charge_total = total_items * delivery_charge
            charges['Delivery'] = delivery_charge_total.quantize(Decimal('0.01'))
        else:
            charges['Delivery'] = Decimal('0')

        for key, value in charges.items():
            final_value += value

        discount_percentage = round(float((discount_amount / gross_value) * 100), 2) if gross_value > 0 else 0

        result = {
            'products': products,
            'total_items': total_items,
            'gross_value': "{:.2f}".format(float(gross_value)),
            'our_price': "{:.2f}".format(float(our_price)),
            'discount_amount': "{:.2f}".format(float(discount_amount)),
            'discount_percentage': "{:.2f}".format(discount_percentage),
            'charges': {k: "{:.2f}".format(float(v)) for k, v in charges.items()},
            'final_value': "{:.2f}".format(float(final_value)),
        }

        return result

    class Meta:
        model = Products
        fields = [
            "products_data",
        ]