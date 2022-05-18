from django.db.models.signals import post_save
from django.contrib.auth.models import Group, User

from .models import Customer


def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

    print("The decorator ran")


post_save.connect(create_customer_profile, sender=User)
