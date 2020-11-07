from django.shortcuts import render
from django.contrib import messages                       
from django.shortcuts import render, get_object_or_404, redirect                      
from django.views.generic import ListView, DetailView                                            
from .models import Cart, CartItem,Product,Profile,OrderItem,OrderItem,Category,Customer,Admin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required


# Create your views here.
class HomeView(ListView):
    model = Product
    template_name = "home.html"

class ProductView(DetailView):
    model = Product
    template_name = "product.html"


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk = pk )
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    if order_qs.exists() :
        order = order_qs[0]
        
        if order.items.filter(item__pk = item.pk).exists() :
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added quantity Item")
            return redirect("core:product", pk = pk)

        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
            return redirect("core:product", pk = pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
        return redirect("core:product", pk = pk)

            # remove from cart
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \""+order_item.item.item_name+"\" remove from your cart")
            return redirect("core:product")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("core:product", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("core:product", pk = pk)

@login_required
def cart_detail(request):

    cart = Cart.objects.get(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)

        products = products.filter(category=category)
    page = request.GET.get('page')
    paginator = Paginator(products, 6)
    try:
        products = paginator.page(page)

    except PageNotAnInteger:
        products = paginator.page(1)

    except EmptyPage:
        products = paginator.page(1)
    is_authenticated = request.user.is_authenticated
    print(is_authenticated)
    if is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user)

        return render(
            request,
            'shop/product/list.html',
            {
                'category': category,
                'categories': categories,
                'products': products,
                'wishlist': wishlist
            }
        )

    else:
        return render(
            request,
            'shop/list.html',
            {
                'category': category,
                'categories': categories,
                'products': products,
            }
        )


def product_search(request):
    results = None
    try:
        query = request.POST['query']
        results = Product.objects.filter(name__icontains=query) |\
            Product.objects.filter(description__icontains=query)
        page = request.GET.get('page')
        paginator = Paginator(results, 6)
        try:
            results = paginator.page(page)

        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:

            results = paginator.page(1)

        wishlist = None
        return render(
            request,
            'shop/list.html',
            {'products': results, 'wishlist': wishlist}
        )
    except KeyError:
        wishlist = None
        "KeyError"
        return render(
            request,
            'shop/list.html',
            {'products': results, 'wishlist': wishlist}
        )


def product_detail(request, id, slug):

    product = get_object_or_404(
        Product,
        id=id,
        slug=slug,
        available=True
    )

    return render(
        request,
        'shop/detail.html',
        {'product': product}
    )

def order_save(request):
    order = Order.objects.create(user=request.user)
    cart = Cart.objects.get(user=request.user)
    order.save()
    for item in cart.items.all():
        orderItem, created = OrderItem.objects.update_or_create(
            order=order, product=item.product, price=item.price, quantity=item.quantity)
        order.order_items.add(orderItem)
    order.address = request.POST['address']
    order.postal_code = request.POST['zip']
    order.country = request.POST['country']
    order.state = request.POST['state']
    order.save()
    
    return redirect('../../payment/'+str(order.id)+'/process')


def order_create(request):


    profile = get_object_or_404(Profile, user=request.user)
    cart = Cart.objects.get(user=request.user)
    
    return render(request, 'orders/order_list.html', {'cart': cart, 'profile': profile})
