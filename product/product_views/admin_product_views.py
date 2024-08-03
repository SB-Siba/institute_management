from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.conf import settings
from helpers import utils
from os.path import join
import json
from product.models import Category,Products,SimpleProduct,ImageGallery

from product import forms
import os
from django.core.files.storage import default_storage

app = "product/"





@method_decorator(utils.super_admin_only, name='dispatch')
class CategoryList(View):
    model = Category
    template = app + "admin/category_list.html"
    form_class = forms.CategoryEntryForm
    def get(self, request):
        catagory_list = self.model.objects.all().order_by('-id')
        context = {
            "form": self.form_class,
            "catagory_list":catagory_list,
        }
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, f"{request.POST['title']} is added to the list.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

        return redirect("product:category_list")

@method_decorator(utils.super_admin_only, name='dispatch')
class CatagoryAdd(View):
    model = Category
    form_class = forms.CategoryEntryForm
    template = app + "admin/category_add.html"

    def get(self, request):
        category_list = self.model.objects.all().order_by('-id')
        context = {
            "category_list": category_list,
            "form": self.form_class,
        }
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category added successfully.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

        return redirect("product:category_list")


@method_decorator(utils.super_admin_only, name='dispatch')
class CategoryUpdate(View):
    model = Category
    form_class = forms.CategoryEntryForm
    template = app + "admin/category_update.html"  # Adjust template path as needed

    def get(self, request, category_id):
        category = get_object_or_404(self.model, id=category_id)
        form = self.form_class(instance=category)
        return render(request, self.template, {'form': form})

    def post(self, request, category_id):
        category = get_object_or_404(self.model, id=category_id)
        form = self.form_class(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"{category.title} updated successfully.")
            return redirect("product:category_update", category_id=category_id)
        else:
            messages.error(request, "Form is not valid. Please check the errors.")
            return render(request, self.template, {'form': form})


@method_decorator(utils.super_admin_only, name='dispatch')
class CatagotyDelete(View):
    model = Category
    form_class = forms.CategoryEntryForm
    template = app + "admin/category_update.html"

    def get(self,request, catagory_id):
        catagory = self.model.objects.get(id= catagory_id).delete()
        messages.info(request, "Catagory is deleted successfully....")
        return redirect("product:category_list")



@method_decorator(utils.super_admin_only, name='dispatch')
class ProductAdd(View):
    model = Products
    form_class = forms.ProductForm
    template = app +"admin/product_add.html"  # Adjust path if necessary

    
    def get(self, request):
        form = self.form_class()
        simple_product_formset = forms.SimpleProductFormSet(queryset=SimpleProduct.objects.none())

        context = {
            "form": form,
            "simple_product_formset": simple_product_formset,
        }
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        simple_product_formset = forms.SimpleProductFormSet(request.POST, request.FILES)

        if form.is_valid() and simple_product_formset.is_valid():
            try:
                # Save the product
                product = form.save(commit=False)
                product.save()

                # Save SimpleProduct instances
                simple_products = simple_product_formset.save(commit=False)
                for simple_product in simple_products:
                    simple_product.product_sku_no = product
                    simple_product.save()

                messages.success(request, "Product is added successfully.")
                return redirect("product:product_list")

            except Exception as e:
                print("Error saving product:", e)
                messages.error(request, f"Error saving product: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            for form_error in simple_product_formset.errors:
                for field, errors in form_error.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        context = {
            "form": form,
            "simple_product_formset": simple_product_formset,
        }

        return render(request, self.template, context)



@method_decorator(utils.super_admin_only, name='dispatch')
class ProductUpdate(View):
    model = Products
    form_class = forms.ProductForm
    template = app + "admin/product_update.html"

    def get(self, request, pk):
        product = get_object_or_404(self.model, pk=pk)
        
        # Initialize forms with the product instance
        form = self.form_class(instance=product)
        simple_product_formset = forms.SimpleProductFormSet(instance=product)
        image_gallery_form = forms.ImageGalleryForm(instance=product.imagegallery_set.first())

        context = {
            "form": form,
            "simple_product_formset": simple_product_formset,
            "image_gallery_form": image_gallery_form,
            "product": product,
        }
        return render(request, self.template, context)

    def post(self, request, pk):
        product = get_object_or_404(self.model, pk=pk)
        form = self.form_class(request.POST, request.FILES, instance=product)
        simple_product_formset = forms.SimpleProductFormSet(request.POST, request.FILES, instance=product)
        image_gallery_form = forms.ImageGalleryForm(request.POST, request.FILES, instance=product.imagegallery_set.first())

        if form.is_valid() and simple_product_formset.is_valid() and image_gallery_form.is_valid():
            try:
                product = form.save(commit=False)
                product.save()

                simple_products = simple_product_formset.save(commit=False)
                for simple_product in simple_products:
                    simple_product.product_sku_no = product
                    simple_product.save()

                image_files = request.FILES.getlist('images')
                if image_files:
                    image_paths = []
                    for image_file in image_files:
                        file_path = default_storage.save(f'product_images/{image_file.name}', image_file)
                        image_paths.append(file_path)

                    image_gallery = image_gallery_form.save(commit=False)
                    image_gallery.simple_product = simple_products[0]
                    image_gallery.images = image_paths
                    image_gallery.save()

                messages.success(request, "Product updated successfully.")
                return redirect("product:product_list")

            except Exception as e:
                print("Error updating product:", e)
                messages.error(request, f"Error updating product: {str(e)}")
        else:
            messages.error(request, "There were errors with the form. Please check the fields and try again.")

        return render(request, self.template, {
            "form": form,
            "simple_product_formset": simple_product_formset,
            "image_gallery_form": image_gallery_form,
            "product": product,
        })
@method_decorator(utils.super_admin_only, name='dispatch')
class ProductDelete(View):
    model = Products

    def get(self,request, product_uid):
        product = self.model.objects.get(uid = product_uid)
        product.delete()
        messages.info(request, 'Product is deleted succesfully......')

        return redirect("product:product_list")


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductList(View):
    model = Products
    template = app + "admin/product_list.html"

    def get(self, request):
        product_list = self.model.objects.order_by('-id')
        print(product_list)
        paginated_data = utils.paginate(request, product_list, 50)

        context = {
            "product_list": product_list,
            "data_list": paginated_data,
            "MEDIA_URL": settings.MEDIA_URL
        }
        return render(request, self.template, context)


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductSearch(View):
    model = Products
    form_class = forms.ProductForm
    template = app + "admin/product_list.html"

    def post(self,request):
        filter_by = request.POST.get("filter_by")
        query = request.POST.get("query")
        product_list = []
        if filter_by == "uid":
            product_list = self.model.objects.filter(uid = query)
        else:
            product_list = self.model.objects.filter(name__icontains = query)

        paginated_data = utils.paginate(
            request, product_list, 50
        )
        context = {
            "form": self.form_class,
            "product_list":product_list,
            "data_list":paginated_data,
            "MEDIA_URL":settings.MEDIA_URL
        }
        return render(request, self.template, context)


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductFilter(View):
    model = Products
    template = app + "admin/product_list.html"

    def get(self,request):
        print("HIIIIII")
        filter_by = request.GET.get("filter_by")
        print(filter_by)
        if filter_by == "trending":
            product_list = self.model.objects.filter(trending="yes").order_by('-id')
            print(product_list)

        elif filter_by == "show_as_new":
            product_list = self.model.objects.filter(show_as_new="yes").order_by('-id')

        elif filter_by == "display_as_bestseller":
            product_list = self.model.objects.filter(display_as_bestseller="yes").order_by('-id')

        elif filter_by == "hide":
            product_list = self.model.objects.filter(hide="yes").order_by('-id')        

        else:
            product_list = self.model.objects.filter().order_by('-id')

        paginated_data = utils.paginate(
            request, product_list, 50
        )
        for product in product_list:
            print(product.images)
        context = {
            "product_list":product_list,
            "data_list":paginated_data,
            "MEDIA_URL":settings.MEDIA_URL
        }
        return render(request, self.template, context)