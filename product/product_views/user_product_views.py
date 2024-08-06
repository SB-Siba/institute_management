from django.shortcuts import render, get_object_or_404
from django.views import View
from product.models import Products, Category,SimpleProduct,ImageGallery
from wishlist.models import WshList
from django.conf import settings

app = 'product/'

class ShowProductsView(View):
    template = app + 'user/productofcategory.html'

    def get(self, request, category_name):
        user = request.user

        # Get the category object for the given category_name
        category_obj = get_object_or_404(Category, title=category_name)

        # Get products for this category
        products_for_this_category = Products.objects.filter(
            category=category_obj
        ).prefetch_related('simple_products')

        return render(request, self.template, {
            'products_for_this_category': products_for_this_category,
            'category_obj': category_obj,
            'user': user,
            "MEDIA_URL": settings.MEDIA_URL,
        })

class ProductDetailsSmipleView(View):
    template_name = app + 'user/product_details.html'

    def get(self, request, p_id):
        user = request.user
        category_obj = Category.objects.all()
        product_obj = get_object_or_404(Products, id=p_id)
        wishlist_items = []        
        similar_product_list = Products.objects.filter(category=product_obj.category).exclude(id=product_obj.id)[:5]
        simple_product = SimpleProduct.objects.filter(product_sku_no=product_obj).first()
        image_gallery = ImageGallery.objects.filter(simple_product=simple_product).first() if simple_product else None
        
        
        if user.is_authenticated:
            wishlist = WshList.objects.filter(user=user).first()
            wishlist_items = wishlist.products.all() if wishlist else []

        context = {
            'user': user,
            'category_obj': category_obj,
            'product_obj': product_obj,
            'simple_product': simple_product,
            'image_gallery': image_gallery,
            'similar_product_list': similar_product_list,  # Corrected key name
            'wishlist_items': wishlist_items,
            'MEDIA_URL': settings.MEDIA_URL,
        }

        return render(request, self.template_name, context)


# class AllTrendingProductsView(View):
#     template = app + 'user/trending_products.html'

#     def get(self, request):
#         trending_products = Products.objects.filter(trending="yes")
#         trending_list = [(product, product.discount_percentage) for product in trending_products]
#         context = {
#             'trending_products': trending_list,
#             'MEDIA_URL': settings.MEDIA_URL,
#         }

#         return render(request, self.template, context)



# class AllNewProductsView(View):
#     template_name = app + "new_products.html"

#     def get(self, request):
#         new_products = Products.objects.filter(show_as_new=True)
#         context = {
#             'new_products': new_products,
#             'MEDIA_URL': settings.MEDIA_URL,
#         }
#         return render(request, self.template_name, context)