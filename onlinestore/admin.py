from django.contrib import admin
# from .models import Order, OrderItem, Category, Admin, Product, Profile, Customer, CartItem, CartItem,
from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)


