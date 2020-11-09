from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url,include
from django.urls import path
from . import views
from .views import (
    remove_from_cart,
    add_to_cart,
    ProductView,
    HomeView,
    OrderDetailView
)

app_name = 'onlinestore'


urlpatterns = [

    path(r'', include('django.contrib.auth.urls')),
    path('signup', views.signup, name='signup'),
    path('detail_profile', views.detail_profile, name='detail_profile'),
    path('', HomeView.as_view(), name='home'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('', views.product_list, name='product_list'),
    path('search', views.product_search, name='product_search'),
    path('(?P<category_slug>[-\w]+)/$',
        views.product_list, name='product_list_by_category'),
    path('products/', ItemListView.as_view(), name='product-list'),
    path('products/<pk>/', ItemDetailView.as_view(), name='product-detail'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('checkout/', PaymentView.as_view(), name='checkout'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('(?P<id>\d+)/(?P<slug>[-\w]+)/$',views.product_detail, name='product_detail'),
    path('search', views.product_search, name='product_search'),
    path('(?P<category_slug>[-\w]+)/$',
        views.product_list, name='product_list_by_category'),
    path('(?P<id>\d+)/(?P<slug>[-\w]+)/$',views.product_detail, name='product_detail'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('order-items/<pk>/delete/',
         OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('order-item/update-quantity/',
         OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    url(r'^create/$', views.order_create, name='order_create'),
    url(r'^process/$', views.order_save, name='order_save'),


]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)