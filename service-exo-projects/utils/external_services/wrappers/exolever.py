from django.conf import settings

from ..mixins import ExternalServiceMixin
from ..urls import reverse


class ExOLeverServiceWrapper(ExternalServiceMixin):
    host = settings.EXOLEVER_HOST
    customers_url = reverse('exo-lever-customer-list')
    partners_url = reverse('exo-lever-partner-list')

    def get_customers(self):
        return self._do_request(self.customers_url)

    def get_partners(self):
        return self._do_request(self.partners_url)


exolever_wrapper = ExOLeverServiceWrapper()
