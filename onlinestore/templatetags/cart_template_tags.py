# from django import template
# from cart_item_count import 
# from django.db import models
# from . models import Order
# from onlinestore.models import Order
# import datetime

# register = template.Library()


# @register.filter
# def cart_item_count(user):
#     if user.is_authenticated:
#         qs = Order.objects.filter(user=user, ordered=False)
#         if qs.exists():
#             return qs[0].items.count()
#     return 0