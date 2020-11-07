from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url,include
from django.urls import path
from . import views
from .views import (
    remove_from_cart,
    add_to_cart,
    ProductView,
    HomeView
)

app_name = 'onlinestore'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('', views.product_list, name='product_list'),
    path('search', views.product_search, name='product_search'),
    path('(?P<category_slug>[-\w]+)/$',
        views.product_list, name='product_list_by_category'),
    path('(?P<id>\d+)/(?P<slug>[-\w]+)/$',views.product_detail, name='product_detail'),
    path('search', views.product_search, name='product_search'),
    path('(?P<category_slug>[-\w]+)/$',
        views.product_list, name='product_list_by_category'),
    path('(?P<id>\d+)/(?P<slug>[-\w]+)/$',views.product_detail, name='product_detail'),
    url(r'^create/$', views.order_create, name='order_create'),
    url(r'^process/$', views.order_save, name='order_save'),


]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)