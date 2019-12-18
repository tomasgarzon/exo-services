# -*- coding: utf-8 -*-
import factory

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from utils.faker_factory import faker


class FakeUserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    email = factory.LazyAttribute(lambda x: faker.email())
    password = '123456'
    last_login = now()
    is_active = True
    is_superuser = False
    is_staff = False
