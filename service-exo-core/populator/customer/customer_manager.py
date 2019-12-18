from singleton_decorator import singleton

from customer.models import Customer

from populate.populator.manager import Manager
from .customer_builder import CustomerBuilder


@singleton
class CustomerManager(Manager):

    model = Customer
    attribute = 'name'
    builder = CustomerBuilder
    files_path = '/customer/files/'
