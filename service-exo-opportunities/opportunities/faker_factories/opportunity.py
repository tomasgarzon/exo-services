import factory
import factory.fuzzy
import datetime

from django.conf import settings

from exo_role.models import CertificationRole, ExORole
from utils.faker_factory import faker

from ..models import Opportunity


class FakeOpportunityFactory(factory.django.DjangoModelFactory):

    title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=20))
    description = factory.LazyAttribute(lambda x: faker.text())
    location = factory.LazyAttribute(
        lambda x: '{}, {}'.format(faker.city(), faker.country()))
    exo_role = factory.LazyAttribute(lambda o: ExORole.objects.get(
        code=settings.EXO_ROLE_CODE_SPRINT_COACH))
    certification_required = factory.LazyAttribute(lambda o: CertificationRole.objects.get(
        code=settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH))
    start_date = factory.fuzzy.FuzzyDate(datetime.date.today())
    deadline_date = factory.fuzzy.FuzzyDate(datetime.date.today())
    duration_unity = factory.fuzzy.FuzzyChoice(
        dict(settings.OPPORTUNITIES_DURATION_UNITY_CHOICES).keys(),
    )
    duration_value = faker.random_digit_not_null()
    entity = factory.LazyAttribute(lambda x: faker.company())
    keywords = []
    languages = []
    budget = factory.LazyAttribute(lambda x: faker.pyint())
    budget_currency = settings.OPPORTUNITIES_CH_CURRENCY_DOLLAR
    virtual_budget = factory.LazyAttribute(lambda x: faker.pyint())
    virtual_budget_currency = settings.OPPORTUNITIES_CH_CURRENCY_EXOS

    class Meta:
        model = Opportunity

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)

        if not kwargs.get('user_from'):
            raise Exception('User is required')

        # The default would use ``manager.create(*args, **kwargs)``
        budgets = []

        if kwargs.get('budget'):
            budgets.append({
                'budget': kwargs.get('budget'),
                'currency': kwargs.get('budget_currency')
            })

        if kwargs.get('virtual_budget'):
            budgets.append({
                'budget': kwargs.get('virtual_budget').__str__(),
                'currency': kwargs.get('virtual_budget_currency')
            })

        kwargs['budgets'] = budgets

        return manager.create_opportunity(*args, **kwargs)
