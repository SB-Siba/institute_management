from django.contrib import admin

from . import models


@admin.register(models.Category)
class ProductsAdmin(admin.ModelAdmin):
    search_fields = ("id","title__icontains")
    list_display = ("title","id")
