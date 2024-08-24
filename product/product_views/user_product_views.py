from django.shortcuts import render, get_object_or_404,redirect
from django.views import View
from app_common import models
from django.contrib import messages
from product.models import Products, Category,SimpleProduct,ImageGallery,ProductReview
from django.db.models import Avg
from wishlist.models import WshList
from product.forms import ProductReviewForm
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
        )

        simple_products = []
        for product in products_for_this_category:
            simple_products_for_product = SimpleProduct.objects.filter(product=product)
            for simple_product in simple_products_for_product:
                image_gallery = ImageGallery.objects.filter(simple_product=simple_product).first()
                images = image_gallery.images if image_gallery else []
                videos = image_gallery.video if image_gallery else []
                simple_products.append({
                    'product': product,
                    'simple_product': simple_product,
                    'images': images,
                    'videos': videos
                })

        return render(request, self.template, {
            'simple_products': simple_products,
            'category_obj': category_obj,
            'user': user,
            "MEDIA_URL": settings.MEDIA_URL,
        })

class ProductDetailsSmipleView(View):
    template_name = app + 'user/product_details.html'

    def get(self, request, p_id):
        user = request.user
        product = get_object_or_404(Products, id=p_id)
        simple_product = SimpleProduct.objects.get(product=product)
        image_gallery = ImageGallery.objects.filter(simple_product=simple_product).first()
        reviews = ProductReview.objects.filter(product=product, approved=True).order_by('-created_at')
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        average_rating = round(average_rating, 1)

        # Fetch similar products
        similar_product_list = Products.objects.filter(category=product.category).exclude(id=product.id)[:5]
        similar_simple_products = []
        for similar_product in similar_product_list:
            try:
                simple = SimpleProduct.objects.get(product=similar_product)
                similar_simple_products.append({
                    'product': similar_product,
                    'simple_product': simple
                })
            except SimpleProduct.DoesNotExist:
                continue

        # Get wishlist items
        wishlist_items = []
        if user.is_authenticated:
            wishlist = WshList.objects.filter(user=user).first()
            wishlist_items = wishlist.products.all() if wishlist else []

        form = ProductReviewForm()

        context = {
            'user': user,
            'product_obj': product,
            'simple_product': simple_product,
            'image_gallery': image_gallery,
            'reviews': reviews,
            'average_rating': average_rating,
            'similar_simple_products': similar_simple_products,
            'wishlist_items': wishlist_items,
            'form': form,
            'MEDIA_URL': settings.MEDIA_URL,
            'star_range': range(1, 6),  # Add star range to context
        }

        return render(request, self.template_name, context)

    def post(self, request, p_id):
        product = get_object_or_404(Products, id=p_id)
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted and is awaiting approval.")
            return redirect('product:product_detail', p_id=p_id)
        else:
            simple_product = SimpleProduct.objects.get(product=product)
            image_gallery = ImageGallery.objects.filter(simple_product=simple_product).first()
            reviews = ProductReview.objects.filter(product=product, approved=True)
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            average_rating = round(average_rating, 1)

            similar_product_list = Products.objects.filter(category=product.category).exclude(id=product.id)[:5]
            similar_simple_products = []
            for similar_product in similar_product_list:
                try:
                    simple = SimpleProduct.objects.get(product=similar_product)
                    similar_simple_products.append({
                        'product': similar_product,
                        'simple_product': simple
                    })
                except SimpleProduct.DoesNotExist:
                    continue

            wishlist_items = []
            if request.user.is_authenticated:
                wishlist = WshList.objects.filter(user=request.user).first()
                wishlist_items = wishlist.products.all() if wishlist else []

            context = {
                'user': request.user,
                'product_obj': product,
                'simple_product': simple_product,
                'image_gallery': image_gallery,
                'reviews': reviews,
                'average_rating': average_rating,
                'similar_simple_products': similar_simple_products,
                'wishlist_items': wishlist_items,
                'form': form,
                'MEDIA_URL': settings.MEDIA_URL,
                'star_range': range(1, 6),  # Add star range to context
            }
            return render(request, self.template_name, context)   


class AllTrendingProductsView(View):
    template_name = app + 'user/trending_products.html'

    def get(self, request):
        trending_products = Products.objects.filter(trending="yes")
        
        context = {
            'trending_products': trending_products,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template_name, context)



class AllNewProductsView(View):
    template_name = app + "user/new_product.html"

    def get(self, request):
        new_products = Products.objects.filter(show_as_new="yes")
        
        context = {
            'new_products': new_products,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template_name, context)

