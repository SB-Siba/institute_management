from django.db import models
import io
from PIL import Image
import os
import uuid
from django.core.files import File
from django.core.files.base import ContentFile
from helpers import utils
from django.template.defaultfilters import slugify



def document_path(self, filename):
    basefilename, file_extension= os.path.splitext(filename)
    myuuid = uuid.uuid4()
    return 'files/{basename}{randomstring}{ext}'.format(basename= basefilename, randomstring= str(myuuid), ext= file_extension)
class Category(models.Model):
    YESNO = (
        ("yes","yes"),
        ("no","no")
    )
    title=models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)

    description=models.TextField()
    image = models.ImageField(upload_to='category/', blank=True, null=True)
    hide = models.CharField(max_length= 255, choices= YESNO ,default="no")

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



class Products(models.Model):
    YESNO = (
        ("yes","yes"),
        ("no","no")
    )
    
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    uid=models.CharField(max_length=255, null=True, blank=True)
    sq_no=models.CharField(max_length=255, null=True, blank=True)
    name=models.CharField(max_length=255, null=True, blank=True, unique=True)
    brand=models.CharField(max_length=255, null=True, blank=True)

    product_max_price=models.FloatField(default=0.0,null=True, blank=True)
    product_discount_price=models.FloatField(default=0.0,null=True, blank=True)

    product_short_description=models.TextField(null=True, blank=True)
    product_long_description=models.TextField(null=True, blank=True)
    stock=models.IntegerField(default=1, blank=True, null=True)
    available=models.IntegerField(null=True, blank=True)
    images = models.JSONField(default=list, blank=True, null=True)
    trending = models.CharField(max_length= 255, choices= YESNO, default="no") 
    show_as_new = models.CharField(max_length= 255, choices= YESNO ,default="no")
    display_as_bestseller = models.CharField(max_length= 255, choices= YESNO ,default="no")

    @property
    def discount_percentage(self):
        if self.product_max_price and self.product_discount_price:
            discount = self.product_max_price - self.product_discount_price
            percentage = discount / self.product_max_price * 100
            return int(percentage)


    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = utils.get_rand_number(5)
        if self.stock:
            self.available = self.stock

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"