from django.shortcuts import render, get_object_or_404
from django.views import View
from product.models import Products, Category
from wishlist.models import WshList
from django.conf import settings

app = 'product/'


class AllCategoriesView(View):
    template = app + "user/all_categories.html"

    def get(self, request):
        category_obj = Category.objects.all()

        context = {
            'category_obj':category_obj,
        }
        return render(request, self.template,context)


class ShowProductsView(View):
    template = app + 'user/productofcategory.html'

    def get(self, request, category_name):
        user = request.user

        # Get the category object for the given category_name
        category_obj = get_object_or_404(Category, title=category_name)

        # Get products for this category
        products_for_this_category = Products.objects.filter(category=category_obj, stock__gt=0)

        return render(request, self.template, {
            'products_for_this_category': products_for_this_category,
            'category_obj': category_obj,
            'user': user,
            "MEDIA_URL": settings.MEDIA_URL,
        })

class ProductDetailsView(View):
    template_name = app + 'user/product_details.html'

    def get(self, request, p_id):
        user = request.user
        category_obj = Category.objects.all()
        product_obj = get_object_or_404(Products, id=p_id)
        wishlist_items = []
        if user.is_authenticated:
            wishlist = WshList.objects.filter(user=request.user).first()
            wishlist_items = wishlist.products.all() if wishlist else []

        context = {
            'user': user,
            'category_obj': category_obj,
            'product_obj': product_obj,
            'similar_product_list': [],  # This can be populated based on your logic
            'wishlist_items': wishlist_items,
            'MEDIA_URL': settings.MEDIA_URL,
        }

        return render(request, self.template_name, context)