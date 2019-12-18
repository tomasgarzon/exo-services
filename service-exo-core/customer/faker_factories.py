# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from factory import django
import factory

# Project Library
from entity.faker_factories import FakeEntityFactoryMixin, FakeContactFactoryMixin

from .models import Customer


@factory.django.mute_signals(post_save)
class FakeCustomerFactory(FakeEntityFactoryMixin, FakeContactFactoryMixin, django.DjangoModelFactory):

    class Meta:
        model = Customer
