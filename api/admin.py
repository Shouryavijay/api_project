from django.contrib import admin
from .models import Note, Product, Order, ScrapedItem

admin.site.register(Note)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(ScrapedItem)
