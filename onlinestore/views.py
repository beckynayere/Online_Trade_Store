from django.shortcuts import render
from django.contrib import messages                       
from django.shortcuts import render, get_object_or_404, redirect                      
from django.views.generic import ListView, DetailView                                            
from .models import Cart, CartItem,Product,Profile,OrderItem,OrderItem,Category,Customer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, View, OrderDetailView
# from django.views.generic.base import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import OrderSerializer,ItemSerializer
# from django.forms import forms
from .forms import PaymentForm,CouponForm, RefundForm, PaymentForm
from django.forms import forms as SignUpForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
class HomeView(ListView):
    model = Product
    template_name = "home.html"

class ProductView(DetailView):
    model = Product
    template_name = "product.html"

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.profile.full_name = form.cleaned_data.get('full_name')
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.profile.full_name = form.cleaned_data.get('full_name')
            user.profile.gender = form.cleaned_data.get('gender')
            user.email = form.cleaned_data.get('email')

            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            # login(request, user)
            return redirect('shop:product_list')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def detail_profile(request):
    return render(request, 'accounts/detail_profile.html')

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
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

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



@login_required
def cart_add(request, product_id, product_qty=None):
    obj, created = Cart.objects.update_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    item, itemCreated = CartItem.objects.update_or_create(
        cart=obj, product=product)
    item.price = product.price
    if(itemCreated == False):
        item.quantity = item.quantity+1
    # if item.quantity = request.GET['q']

    obj.items.add(item)
    item.save()
    obj.save()
    return redirect('cart:cart_detail')


@login_required
def cart_add_q(request, product_id, product_qty=None):
    obj, created = Cart.objects.update_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    item, itemCreated = CartItem.objects.update_or_create(
        cart=obj, product=product)
    item.price = product.price

    # if item.quantity = request.GET['q']
    item.quantity = request.GET['q']
    if request.GET['q'] == "0":
        item.delete()
    else:
        obj.items.add(item)
        item.save()
        obj.save()
    return redirect('cart:cart_detail')

    # form = CartAddProductForm(request.POST)
    # if form.is_valid():
    #     cd = form.cleaned_data
    #     item.quantity=cd['quantity'],

def cart_remove(request, product_id):
    obj, created = Cart.objects.update_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cartItems = CartItem.objects.filter(cart=obj, product=product)
    cartItems.delete()
    return redirect('cart:cart_detail')


@login_required
def cart_detail(request):

    cart = Cart.objects.get(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")

class OrderItemDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = OrderItem.objects.all()

class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                return Response(status=HTTP_200_OK)
            else:
                return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)
