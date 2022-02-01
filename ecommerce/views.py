from django.shortcuts import render

# Create your views here.


def store(request):

    context = {}

    return render(request, 'ecommerce/store.html', context)


def checkout(request):

    context = {}

    return render(request, 'ecommerce/checkout.html', context)


def cart(request):

    context = {}

    return render(request, 'ecommerce/cart.html', context)


def home(request):

    context = {}

    return render(request, 'ecommerce/main.html', context)
