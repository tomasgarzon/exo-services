from .entity_user import EntityUserQuerySet


class CustomerUserQuerySet(EntityUserQuerySet):
    def filter_by_customer(self, customer):
        return self.filter(customer=customer)

    def customers(self):
        from customer.models import Customer  # avoid cycle
        customer_ids = self.values_list('customer_id', flat=True)
        return Customer.objects.filter(id__in=customer_ids)
