from singleton_decorator import singleton

from payments.models import Payment

from populate.populator.manager import Manager
from .payments_builder import PaymentBuilder


@singleton
class PaymentsManager(Manager):
    model = Payment
    attribute = 'concept'
    builder = PaymentBuilder
    files_path = '/payments/files/'
