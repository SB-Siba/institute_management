from django import forms
from django.forms import inlineformset_factory
from product.models import Category,Products,SimpleProduct,ImageGallery

class CategoryEntryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = [
            'title',
            'hide',
            'image'

        ]

    title = forms.CharField(max_length=255)
    title.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    
    image = forms.ImageField(label='image', required=True)
    image.widget.attrs.update({'class': 'form-control','type':'file'})

    hide = forms.ChoiceField(choices= Category.YESNO)
    hide.widget.attrs.update({'class': 'form-control','type':'text'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = [
            'category', 'sku_no', 'name', 'brand', 'image', 
            'product_short_description', 'product_long_description', 
            'trending', 'show_as_new', 'product_type'
        ]
        widgets = {
            'trending': forms.RadioSelect(choices=Products.YESNO),
            'show_as_new': forms.RadioSelect(choices=Products.YESNO),
            'product_type': forms.RadioSelect(choices=Products.PRODUCT_TYPE_CHOICES),
        }

class SimpleProductForm(forms.ModelForm):
    class Meta:
        model = SimpleProduct
        fields = [
            'product_sku_no', 'product_max_price', 'product_discount_price', 'stock'
        ]

class ImageGalleryForm(forms.ModelForm):
    class Meta:
        model = ImageGallery
        fields = ['simple_product', 'videos'] 

SimpleProductFormSet = inlineformset_factory(
    Products, SimpleProduct, form=SimpleProductForm, extra=1, can_delete=True
)

ImageGalleryFormSet = inlineformset_factory(
    SimpleProduct, ImageGallery, form=ImageGalleryForm, extra=1, can_delete=True
)