from django.db.models import Q, Case, Value, When, BooleanField
from django.conf import settings

from core.models import Language
from core.helpers import COUNTRIES, COUNTRIES_DEFAULT
from exo_activity.models import ExOActivity
from exo_attributes.models import ExOAttribute
from exo_hub.models import ExOHub
from exo_role.models import ExORole, CertificationRole
from industry.models import Industry
from keywords.models import Keyword

from ..api.serializers.filters import (
    ExOHubFilterSerializer,
    ExORoleFilterSerializer,
    CertificationRoleFilterSerializer,
    ExOAttributeFilterSerializer,
    LanguageFilterSerializer,
    IndustryFilterSerializer,
    KeywordFilterSerializer,
    ExOActivityFilterSerializer)


def get_industries_filter_data():
    default_items = Q(name__in=['Communications', 'Computer', 'Consulting', 'Education'])
    queryset = Industry.objects.filter(public=True).exclude(name='')
    queryset = queryset.annotate(
        default=Case(
            When(default_items, then=Value(True)),
            default=False,
            output_field=BooleanField(),
        )
    )

    serializer = IndustryFilterSerializer(
        queryset,
        many=True)

    data = {
        'title': 'ExO Industries',
        'queryparam': 'industries',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_attributes_filter_data():
    queryset = ExOAttribute.objects.all().order_by('name')
    queryset = queryset.annotate(default=Value(True, BooleanField()))

    serializer = ExOAttributeFilterSerializer(
        queryset,
        many=True)

    data = {
        'title': 'ExO Attributes',
        'queryparam': 'attributes',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_roles_filter_data():
    queryset = ExORole.objects.all().filter_by_category_code(settings.EXO_ROLE_CATEGORY_EXO_SPRINT)
    queryset = queryset.annotate(default=Value(True, BooleanField()))

    serializer = ExORoleFilterSerializer(
        queryset,
        many=True)

    data = {
        'title': 'ExO Roles',
        'queryparam': 'roles',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_languages_filter_data():
    default_items = Q(name__in=['French', 'German', 'Spanish'])
    queryset = Language.objects.all()
    queryset = queryset.annotate(
        default=Case(
            When(default_items, then=Value(True)),
            default=False,
            output_field=BooleanField(),
        )
    )

    serializer = LanguageFilterSerializer(
        queryset,
        many=True)

    data = {
        'title': 'Languages',
        'queryparam': 'languages',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_location_filter_data():
    queryset = []

    for country in COUNTRIES:
        data = {
            'name': country,
            'value': country,
            'default': True if country in COUNTRIES_DEFAULT else False,
        }
        queryset.append(data)

    data = {
        'title': 'Location',
        'queryparam': 'location',
        'multiselect': True,
        'items': queryset,
    }

    return data


def get_certifications_filter_data():
    queryset = CertificationRole.objects.all()
    queryset = queryset.annotate(default=Value(True, BooleanField()))

    serializer = CertificationRoleFilterSerializer(
        queryset,
        many=True)

    data = {
        'title': 'Certifications',
        'queryparam': 'certifications',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_hubs_filter_data():
    queryset = ExOHub.objects.all()
    queryset = queryset.annotate(default=Value(True, BooleanField()))

    serializer = ExOHubFilterSerializer(queryset, many=True)

    data = {
        'title': 'Hubs',
        'queryparam': 'hubs',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_technologies_filter_data():
    default_items = Q(name__in=['Blockchain', 'Cryptocurrency', 'Virtual Reality'])
    queryset = Keyword.objects.filter(tags__name__in=[settings.KEYWORDS_CH_TECHNOLOGY]).distinct('name')
    queryset = queryset.annotate(
        default=Case(
            When(default_items, then=Value(True)),
            default=False,
            output_field=BooleanField(),
        )
    )

    serializer = KeywordFilterSerializer(queryset, many=True)

    data = {
        'title': 'Technologies',
        'queryparam': 'technologies',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_activities_filter_data():
    queryset = ExOActivity.objects.all()
    queryset = queryset.annotate(default=Value(True, BooleanField()))

    serializer = ExOActivityFilterSerializer(queryset, many=True)

    data = {
        'title': 'Interests',
        'queryparam': 'activities',
        'multiselect': True,
        'items': serializer.data,
    }

    return data


def get_staff_filter_data():
    items = [
        {
            'name': 'Active',
            'value': settings.ECOSYSTEM_API_STATUS_ACTIVE,
            'default': True,
        },
        {
            'name': 'All',
            'value': settings.ECOSYSTEM_API_STATUS_ALL,
            'default': True,
        },
        {
            'name': 'Inactive',
            'value': settings.ECOSYSTEM_API_STATUS_INACTIVE,
            'default': True,
        }
    ]

    data = {
        'title': 'Staff',
        'queryparam': 'status',
        'multiselect': False,
        'items': items,
    }

    return data
