from ...models import Consultant
from ...forms import ConsultantFilterForm


class NetworkListFilterMixin:
    model = Consultant
    form_class = ConsultantFilterForm
    load_all = False
