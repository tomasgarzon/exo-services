import factory

from factory import fuzzy, DictFactory

from utils.faker_factory import faker

from ..conf import settings


class FakeServiceRequestFactory(DictFactory):
    name = factory.LazyAttribute(lambda x: faker.name())
    last_name = factory.LazyAttribute(lambda x: faker.name())
    email = factory.LazyAttribute(lambda x: faker.email())
    company = factory.LazyAttribute(lambda x: faker.word())
    country = factory.LazyAttribute(lambda x: faker.word())
    position = factory.LazyAttribute(lambda x: faker.word())
    status = fuzzy.FuzzyChoice(dict(settings.MARKETPLACE_CH_STATUS).keys())
    motivation = fuzzy.FuzzyChoice(dict(settings.MARKETPLACE_CH_MOTIVATION).keys())
    goal = fuzzy.FuzzyChoice(dict(settings.MARKETPLACE_CH_GOAL).keys())
    employees = fuzzy.FuzzyChoice(dict(settings.MARKETPLACE_CH_EMPLOYEES_RANGE).keys())
    initiatives = fuzzy.FuzzyChoice(dict(settings.MARKETPLACE_CH_INITIATIVES_RANGE).keys())
    book = fuzzy.FuzzyChoice([True, False])
    comment = factory.LazyAttribute(lambda x: faker.text())
