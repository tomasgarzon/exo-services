from django.conf import settings
from django.contrib.auth import get_user_model

from account_config.models import ConfigParam
from consultant.models import ConsultantExOProfile, Consultant
from core.models import Language
from industry.models import Industry
from keywords.models import Keyword
from exo_area.models import ExOArea
from exo_activity.models import ExOActivity
from exo_attributes.models import ExOAttribute
from exo_hub.models import ExOHub
from ecosystem.models import Member
from relation.models import (
    ConsultantExOAttribute, ConsultantIndustry,
    ConsultantKeyword, ConsultantExOArea)
from populate.populator.common.helpers import find_tuple_values

from ..exo_account.exo_account_builder import ExOAccountBuilder


class ConsultantBuilder(ExOAccountBuilder):
    images_path = '/exo_account/images/'

    def create_object(self):

        user = self.create_user(
            uuid4=self.data.get('uuid'),
            short_name=self.data.get('short_name'),
            full_name=self.data.get('full_name'),
            bio_me=self.data.get('bio_me'),
            groups=self.data.get('groups'),
            time_zone=self.data.get('time_zone'),
            status=self.data.get('status', 'Active'),
            website=self.data.get('website'),
            profile_picture=self.data.get('image'),
            place=self.data.get('place', None))
        self.add_permissions(user, self.data.get('permissions', []))

        consultant = self.create_consultant(
            user=user,
            status=self.data.get('status', 'Active'),
            languages=self.data.get('languages', []),
            exo_areas=self.data.get('exo_areas', []),
            industries=self.data.get('industries', []),
            keywords=self.data.get('keywords', []),
            exo_attributes=self.data.get('exo_attributes', []),
            time_zone=self.data.get('time_zone', None),
            created_by=self.data.get('created_by', None),
            coins=self.data.get('coins', None),
            last_activity=self.data.get('last_activity', None))

        # ExO profile is created by signals, so update it
        self.update_profile(
            profile=consultant.exo_profile,
            personal_mtp=self.data.get('personal_mtp'),
            mtp_mastery=self.data.get('mtp_mastery'),
            availability=self.data.get('availability'))

        contracting_info = self.data.get('contracting_data', None)
        if contracting_info:
            consultant.exo_profile.set_contracting(**contracting_info)

        self.config_account(
            consultant=consultant,
            notifications=self.data.get('user_notifications', []))

        self.update_hubs(
            consultant=consultant,
            hubs=self.data.get('hubs', []))

        self.create_badges(
            user=user,
            badges=self.data.get('badges', []))

        return consultant

    def create_user(self, uuid4, short_name,
                    full_name, bio_me, groups,
                    place, time_zone, status, website, profile_picture=None):
        user = super(ConsultantBuilder, self).create_user(
            uuid=uuid4,
            email='{}@example.com'.format(full_name.replace(' ', '').lower()),
            short_name=short_name,
            full_name=full_name,
            password='.eeepdQA',
            is_superuser=False,
            is_staff=False,
            timezone=time_zone,
            bio_me=bio_me,
            profile_picture=profile_picture)

        self.add_groups(user, self.data.get('groups', []))
        if profile_picture:
            self.update_image(user, profile_picture)
        internal_organization = self.data.get('internal_organization')

        if internal_organization:
            self.update_internal_organization(
                user=user,
                internal_organization=internal_organization)

        place = self.data.get('place', None)

        if place:
            self.update_place(user, place)

        if website:
            user.website = website
            user.save()

        if self.data.get('status', None) == 'Sign Up':
            user.is_active = False
            user.set_unusable_password()
            user.save()

        self.marketplace_agreement(user=user)

        return user

    def create_consultant(
            self, user, status, languages,
            industries, keywords, exo_attributes,
            time_zone, coins, exo_areas, created_by,
            last_activity):

        kwargs = {'coins': coins} if coins else {}
        if created_by is None:
            created_by = get_user_model().objects.filter(is_superuser=True).first()
        consultant = Consultant.objects.create_consultant(
            short_name=user.short_name,
            email=user.email,
            full_name=user.full_name,
            invite_user=created_by,
            registration_process=True,
            waiting_list=False,
            **kwargs)

        if last_activity:
            Member.objects.filter(user=consultant.user).update(
                modified=last_activity)

        self.update_consultant_status(consultant=consultant, status=status)

        for area in exo_areas:
            ConsultantExOArea.objects.create(
                consultant=consultant,
                exo_area=ExOArea.objects.get(
                    name=area))

        for industry in industries:
            ConsultantIndustry.objects.create(
                consultant=consultant,
                level=find_tuple_values(
                    settings.RELATION_INDUSTRIES_CHOICES,
                    industry.get('level'))[0],
                industry=Industry.objects.get(
                    name=industry.get('name')))

        for keyword in keywords:
            ConsultantKeyword.objects.create(
                consultant=consultant,
                level=find_tuple_values(
                    settings.RELATION_KEYWORD_CHOICES,
                    keyword.get('level'))[0],
                keyword=Keyword.objects.get(
                    name=keyword.get('name')))

        # ExO attributes are created by default, so just update it
        for attr in exo_attributes:
            consultant_attribute = ConsultantExOAttribute.objects.get(
                consultant=consultant,
                exo_attribute=ExOAttribute.objects.get(
                    name=attr.get('attribute')))
            consultant_attribute.level = find_tuple_values(
                settings.RELATION_EXO_ATTRIBUTE_CHOICES,
                attr.get('level'))[0]
            consultant_attribute.save(update_fields=['level'])
        return consultant

    def update_profile(self, profile, personal_mtp, mtp_mastery, availability):
        values = {}

        if personal_mtp:
            values.update({'personal_mtp': personal_mtp})

        if mtp_mastery:
            values.update({'mtp_mastery': find_tuple_values(
                settings.CONSULTANT_SKILL_MTP_MASTERY_CHOICES,
                mtp_mastery)[0]})

        if availability:
            values.update({'availability': find_tuple_values(
                settings.CONSULTANT_SKILL_AVAILABILITY,
                availability)[0]})

        ConsultantExOProfile.objects.filter(pk=profile.id).update(**values)

    def config_account(self, consultant, notifications):
        for item in notifications:
            param = ConfigParam.objects.get(name=item)
            param.set_value_for_agent(consultant, True)

    def update_hubs(self, consultant, hubs):
        for h in hubs:
            hub = ExOHub.objects.get(name=h)
            hub.users.create(user=consultant.user)

    def update_consultant_status(self, consultant, status):
        registration_process = consultant.user.registration_process
        if status == 'Agreement':
            self.sign_up(registration_process)
        elif status == 'Welcome Onboarding':
            self.sign_up(registration_process)
            self.agreement(registration_process)
        elif status == 'Active':
            self.sign_up(registration_process)
            self.agreement(registration_process)
            self.welcome_onboarding(registration_process)

    def sign_up(self, registration_process):
        data = {}
        data['email'] = self.data.get('email')
        data['password'] = '.eeepdQA'
        invitation = registration_process.current_step.invitation
        invitation.accept(registration_process.consultant.user, **data)

    def agreement(self, registration_process):
        invitation = registration_process.current_step.invitation
        invitation.accept(registration_process.consultant.user)

    def welcome_onboarding(self, registration_process):
        invitation = registration_process.current_step.invitation
        exo_activities = self.data.get('exo_activities', [])
        languages = self.data.get('languages', [])
        data = {}
        data['exo_activities'] = [ExOActivity.objects.get(name=act) for act in exo_activities]
        data['languages'] = Language.objects.filter(name__in=languages)
        data['full_name'] = self.data.get('full_name')
        data['short_name'] = self.data.get('short_name')
        data['bio_me'] = self.data.get('bio_me')
        data['location'] = self.data.get('place').get('name') if self.data.get('place') else ''
        data['place_id'] = self.data.get('place').get('place_id') if self.data.get('place') else ''
        data['areas'] = []
        data['contracting_data'] = {
            'name': None,
            'address': None,
            'company_name': None
        }
        invitation.accept(registration_process.consultant.user, **data)
