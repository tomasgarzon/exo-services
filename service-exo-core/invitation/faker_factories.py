# -*- coding: utf-8 -*-
# Third Party Library
import factory
from factory import django
from datetime import datetime

# Project Library
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from utils.dates import increase_date

from .conf import settings
from .models import Invitation, InvitationObject, RelatedObjectFake


class FakeInvitationObjectFactory(django.DjangoModelFactory):

    class Meta:
        model = InvitationObject


class FakeInvitationFactory(django.DjangoModelFactory):

    status = factory.fuzzy.FuzzyChoice(
        [x[0] for x in settings.INVITATION_CH_STATUS],
    )

    type = factory.fuzzy.FuzzyChoice(
        [x[0] for x in settings.INVITATION_CH_TYPE],
    )

    user = factory.SubFactory(FakeUserFactory)
    invite_user = factory.SubFactory(FakeUserFactory)

    valid_date = factory.fuzzy.FuzzyDate(
        start_date=datetime.today().date(),
        end_date=increase_date(days=5, date=datetime.today().date()),
    )

    class Meta:
        model = Invitation


class FakeRelatedObjectFactory(django.DjangoModelFactory):
    class Meta:
        model = RelatedObjectFake
