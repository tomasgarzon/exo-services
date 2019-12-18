import uuid
import random

from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import Permission
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist

from populate.populator.builder import Builder
from populate.populator.common.helpers import find_tuple_values
from populator import BASE_DIR

from badge.helpers import update_or_create_badge
from circles.models import Circle
from custom_auth.models import InternalOrganization
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from relation.models import OrganizationUserRole
from agreement.models import Agreement


class ExOAccountBuilder(Builder):
    images_path = '/exo_account/images/'

    def create_object(self):
        user = self.create_user(
            uuid=uuid.UUID('{}'.format(self.data.get('uuid'))),
            is_superuser=self.data.get('is_superuser', False),
            is_staff=self.data.get('is_staff', False),
            is_active=self.data.get('is_active', True),
            email=self.data.get('email'),
            password=self.data.get('password', '.eeepdQA'),
            full_name=self.data.get('full_name'),
            short_name=self.data.get('short_name'),
            date_joined=self.data.get(
                'date_joined',
                timezone.now() - timedelta(days=random.randint(0, 5))
            ),
            profile_picture=self.data.get('image')
        )

        self.add_groups(user, self.data.get('groups', []))
        self.add_permissions(user, self.data.get('permissions', []))
        internal_organization = self.data.get('internal_organization')
        place = self.data.get('place', None)

        if internal_organization:
            self.update_internal_organization(
                user=user,
                internal_organization=internal_organization)

        place = self.data.get('place', None)
        if place:
            self.update_place(user, place)
        if self.data.get('image'):
            self.update_image(user, self.data.get('image'))
        return user

    def create_user(self, **kwargs):
        user = FakeUserFactory.create(**kwargs)

        if user.is_superuser:
            for circle in Circle.objects.all():
                circle.add_user(user)

        return user

    def marketplace_agreement(self, user):
        marketplace_agreement = self.data.get('marketplace_agreement_signed', None)  # noqa
        if marketplace_agreement:
            agreements = Agreement.objects.filter_by_domain_marketplace().filter_by_status_active()  # noqa
            user.sign_agreement(agreements.first())
            user.see_section(settings.EXO_ACCOUNTS_MARKETPLACE_SECTION)

    def update_internal_organization(self, user, internal_organization):
        organization, _ = InternalOrganization.objects.get_or_create(
            name=internal_organization.get('name'))
        status = find_tuple_values(settings.RELATION_ROLE_CH_STATUS,
                                   internal_organization.get('status'))[0]

        OrganizationUserRole.objects.get_or_create(
            user=user,
            organization=organization,
            position=internal_organization.get('position'),
            status=status)

    def update_place(self, user, place):
        user.location = place.get('name', None)
        user.place_id = place.get('place_id', None)
        if user.location and user.place_id:
            user.save(update_fields=['location', 'place_id'])

    def add_groups(self, user, groups):
        for group in groups:
            try:
                my_group = Group.objects.get(name=group)
                my_group.user_set.add(user)
            except ObjectDoesNotExist:
                print('Group {} DoesNotExist')

    def add_permissions(self, user, permissions):
        for codename in permissions:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)

    def update_image(self, user, name):
        file_path = '{}{}'.format(BASE_DIR, self.images_path)
        filename = '{}{}.jpg'.format(file_path, name)
        with open(filename, 'rb') as f:
            content_file = ContentFile(f.read())
        user.profile_picture.save(
            '%s.jpg' % (user.get_letter_initial()),
            content_file,
            save=True,
            default=True,
        )

    def create_badges(self, user, badges):
        for badge in badges:
            item = {
                'name': badge.get('item_name'),
                'date': badge.get('item_date'),
            }

            update_or_create_badge(
                user_from=user,
                user_to=user,
                code=badge.get('code'),
                category=badge.get('category'),
                items=[item],
                description='populator')
