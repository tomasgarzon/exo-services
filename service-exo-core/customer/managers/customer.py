from django.db import models

from entity.managers import EntityManagerMixin

from ..queryset.customer import CustomerQuerySet


class CustomerManager(
    EntityManagerMixin,
    models.Manager
):

    queryset_class = CustomerQuerySet

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)
