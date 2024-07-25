from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.conf import settings
from helpers import utils
from os.path import join
import json
from product import models
from product import forms
import os
from django.core.files.storage import default_storage

app = "product/"

@method_decorator(utils.super_admin_only, name='dispatch')
class CategoryList(View):
    model = models.Category
    form_class = forms.CategoryEntryForm
    template = app + "admin/category_list.html"

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
class CategoryUpdate(View):
    model = models.Category
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
    model = models.Category
    form_class = forms.CategoryEntryForm
    template = app + "admin/category_update.html"

    def get(self,request, catagory_id):
        catagory = self.model.objects.get(id= catagory_id).delete()
        messages.info(request, "Catagory is deleted successfully....")
        return redirect("product:category_list")


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductAdd(View):
    model = models.Products
    form_class = forms.ProductForm
    template = app + "admin/product_add.html"

    def get(self, request):
        form = self.form_class()
        product_list = self.model.objects.all().order_by('-id')
        context = {
            "product_list": product_list,
            "form": form,
        }
        return render(request, self.template, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                images = request.FILES.getlist('images')

                # Validate that at least one image is uploaded
                if not images:
                    messages.error(request, "Please upload at least one image.")
                    return redirect("product:product_add")

                # Save product to obtain an ID
                product.save()

                # Save images and update the product's images field
                image_list = []
                for file in images:
                    file_path = default_storage.save(os.path.join('product_images', file.name), file)
                    image_list.append(file_path.replace("\\", "/"))
                
                product.images = image_list
                product.save()

                messages.success(request, "Product is added successfully.")
            except Exception as e:
                print("Error saving product:", e)
                messages.error(request, f"Error saving product: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

        return redirect("product:product_list")


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductUpdate(View):
    model = models.Products
    form_class = forms.ProductForm
    template = app + "admin/product_update.html"

    def get(self, request, product_uid):
        product = self.model.objects.get(uid=product_uid)
        context = {
            "product": product,
            "form": self.form_class(instance=product),
            "MEDIA_URL":settings.MEDIA_URL
        }
        return render(request, self.template, context)

    def post(self, request, product_uid):
        product = self.model.objects.get(uid=product_uid)
        form = self.form_class(request.POST, request.FILES, instance=product)

        if form.is_valid():
            
            images = request.FILES.getlist('new_images')
            if not product.images:
                if not images:
                    messages.error(request, "Please upload at least one image.")
                    return redirect("product:product_list")
            product = form.save(commit=False)
            # product.save()

            remove_images = request.POST.getlist('remove_images')
            current_images = product.images
            print(f"Remove images {remove_images} \n Current Images {current_images}")
            # Filter out removed images
            new_images = [img for img in current_images if img not in remove_images]

            # Handle adding new images
            new_uploaded_images = request.FILES.getlist('new_images')
            if new_uploaded_images:
                image_list = []
                for file in new_uploaded_images:
                    file_path = default_storage.save(os.path.join('product_images', file.name), file)
                    image_list.append(file_path.replace("\\", "/"))
                new_images.extend(image_list)
            print(f"\nNew List {new_images}")
            # Save the updated product
            
            product.images = new_images  # Convert list back to JSON string
            product.save()

            messages.success(request, 'Product updated successfully.')
            return redirect('product:product_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

        return redirect("product:product_update", product_uid=product_uid)


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductDelete(View):
    model = models.Products

    def get(self,request, product_uid):
        product = self.model.objects.get(uid = product_uid)
        product.delete()
        messages.info(request, 'Product is deleted succesfully......')

        return redirect("product:product_list")


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductList(View):
    model = models.Products
    template = app + "admin/product_list.html"

    def get(self,request):
        product_list = self.model.objects.order_by('-id')
        print(product_list)

        paginated_data = utils.paginate(
            request, product_list, 50
        )
        context = {
            "product_list":product_list,
            "data_list":paginated_data,
            "MEDIA_URL":settings.MEDIA_URL
        }
        return render(request, self.template, context)


@method_decorator(utils.super_admin_only, name='dispatch')
class ProductSearch(View):
    model = models.Products
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
    model = models.Products
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