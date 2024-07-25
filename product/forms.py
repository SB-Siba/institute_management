from django import forms
from helpers import utils
from django.forms.utils import ValidationError

from product import models

class CategoryEntryForm(forms.ModelForm):

    class Meta:
        model = models.Category
        fields = [
            'title',
            'hide',
            'image'

        ]

    title = forms.CharField(max_length=255)
    title.widget.attrs.update({'class': 'form-control','type':'text',"required":"required"})

    
    image = forms.ImageField(label='image', required=True)
    image.widget.attrs.update({'class': 'form-control','type':'file'})

    hide = forms.ChoiceField(choices= models.Category.YESNO)
    hide.widget.attrs.update({'class': 'form-control','type':'text'})



class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Products
        fields = [
            'sq_no',
            'category',
            'name',
            'brand',
            'stock',
            'product_max_price',
            'product_discount_price',
            'product_short_description',
            'product_long_description',
            'trending',
            'show_as_new',  
            
        ]
    sq_no = forms.CharField(max_length=255)
    sq_no.widget.attrs.update({'class': 'form-control', 'type': 'text', "required": "required"})

    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}))
    category.widget.attrs.update({'class': 'form-control', 'type': 'text'})

    name = forms.CharField(max_length=255)
    name.widget.attrs.update({'class': 'form-control', 'type': 'text', "required": "required"})

    brand = forms.CharField(max_length=255, required=False)
    brand.widget.attrs.update({'class': 'form-control', 'type': 'text'})

    product_short_description = forms.CharField(required=True, widget=forms.Textarea(attrs={"class": "form-control", "rows": "2"}))
    product_short_description.widget.attrs.update({'class': 'form-control', 'type': 'text'})

    product_long_description = forms.CharField(required=True, widget=forms.Textarea(attrs={"class": "form-control", "rows": "2"}))
    product_long_description.widget.attrs.update({'class': 'form-control', 'type': 'text'})


    stock = forms.IntegerField(required=False)
    stock.widget.attrs.update({'class': 'form-control', 'type': 'number'})

    

    trending = forms.ChoiceField(choices=models.Products.YESNO, initial='no')
    trending.widget.attrs.update({'class': 'form-control', 'type': 'text', "required": "required"})

    show_as_new = forms.ChoiceField(choices=models.Products.YESNO, initial='no')
    show_as_new.widget.attrs.update({'class': 'form-control', 'type': 'text', "required": "required"})

    product_max_price = forms.IntegerField(required=False)
    product_max_price.widget.attrs.update({'class': 'form-control', 'type': 'text', 'placeholder': 'Enter Market Price'})

    product_discount_price = forms.IntegerField(required=False)
    product_discount_price.widget.attrs.update({'class': 'form-control', 'type': 'text', 'placeholder': 'Enter Your Discounted Price'})
    

    

    def clean(self):
        cleaned_data = super().clean()

        product_max_price = cleaned_data.get('product_max_price')
        product_discount_price = cleaned_data.get('product_discount_price')
        stock = cleaned_data.get('stock')

        if not product_max_price:
            self.add_error('product_max_price', 'Select Max Price.')
        if not product_discount_price:
            self.add_error('product_discount_price', 'Select Discounted Price.')
        if not stock:
            self.add_error('stock', 'Add Stock For Product.')

        return cleaned_data