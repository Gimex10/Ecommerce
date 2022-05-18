from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse
import datetime
import json


from .models import *
from .forms import *
from .utils import *
# Create your views here.

User = get_user_model()


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        password2 = form.cleaned_data.get("password2")

        if password == password2:
            try:
                user = User.objects.create_user(username, email, password)
            except:
                user = None

            if user != None:
                login(request, user)
                return redirect("/store")

            else:
                request.session['registration-error'] = 1

        else:
            # password1 not equal to password2
            print('Passwords do not match')
            # messages ==> Passwords do not match

    return render(request, "ecommerce/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request, user)
            return redirect("/store")

        else:
            # attempt = request.session.get("") or 0
            # request.session['attempt'] = attempt + 1
            # return redirect("/invalid-password")
            request.session['invalid-user'] = 1

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order,
               'cartItems': cartItems, "form": form}
    return render(request, "ecommerce/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("/store")


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()

    context = {'products': products, 'cartItems': cartItems}

    return render(request, 'ecommerce/store.html', context)


def cart(request):

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'ecommerce/cart.html', context)


# @login_required
def checkout(request):

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'ecommerce/checkout.html', context)


def home(request):

    context = {}

    return render(request, 'ecommerce/index.html', context)


def updateItem(request):
    # print("data", request.body.decode('utf-8'))
    data = json.loads(request.body.decode('utf-8'))
    productId = data['productId']
    action = data['action']
    # print('Action:', action)
    # print('Product:', productId)
    # print('data:', data)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    # print('customer', customer)
    # print('product', product)
    # print('product_id', product.id)
    # print('order', order)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    # print('orderItem', orderItem)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
        print("Item added")
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
        print("Item removed")

    # print("orderItem", orderItem)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    print('Data:', data)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    # else:
    #     customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            county=data['shipping']['county'],
            postal_code=data['shipping']['postal_code'],
        )

    return JsonResponse('Payment submitted...', safe=False)
