from django.contrib.auth import get_user_model

import json

from .models import *


User = get_user_model()


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)
    print('This is cart in utils.py line 17 is printing')
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'digital': product.digital,
                'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True

        except:
            pass
    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):

    user = request.user
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    users = User.objects.all()
    # print('Users:', users)

    emails = []
    for i in users:
        emails.append(i.email)
    #     if i.email == email:
    #         print('Email exists')
    #     else:
    #         print('New user')

    if email not in emails:
        print('Not yet a user')

    # customer, created = Customer.objects.get_or_create(user_id=request.user.id)
    customer = Customer.objects.get(user_id=request.user.id)
    # print('Customer:', customer)
    # customer.name = name
    # print('Customer name:', customer.name)

    # customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )
    # print('Order:', order)

    for item in items:

        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product, order=order,
            quantity=item['quantity'],
        )
    return customer, order
