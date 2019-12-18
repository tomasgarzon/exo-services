import requests
import json
import logging

from rest_framework import status

from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger('hubspot')

URL_BASE = 'https://api.hubapi.com'
CONTACT_SECTION = 'contacts/v1'

COMMUNITY_LIFE_CYCLE_LEAD = 'COMMUNITY_LEAD'
COMMUNITY_LIFE_CYCLE_MEMBER = 'COMMUNITY_MEMBER'

ON_BOARDING_ENTRY_POINT_ALREADY_MEMBER = 'INVITATION'

ON_BOARDING_ENTRY_POINT_JOIN = 'JOIN_COMMUNITY_FORM'
ON_BOARDING_ENTRY_POINT_CERTIFIED = 'GET_CERTIFIED_FORM'
ON_BOARDING_ENTRY_POINT_SUMMITS = 'SUMMITS_SIGNUPS'

ON_BOARDING_ENTRY_POINT_CERTIFICATION_LEVEL_1 = 'CERTIFICATION_LEVEL_1_FORM'
ON_BOARDING_ENTRY_POINT_CERTIFICATION_LEVEL_2 = 'CERTIFICATION_LEVEL_2_FORM'
ON_BOARDING_ENTRY_POINT_CERTIFICATION_LEVEL_3 = 'CERTIFICATION_LEVEL_3_FORM'

ON_BOARDING_ENTRY_POINT_BOOKS = 'BOOKS_FORM'
ON_BOARDING_ENTRY_POINT_EXO_CANVAS = 'EXO_CANVAS_FORM'
DEFAULT_ON_BOARDING_ENTRY_POINT = ON_BOARDING_ENTRY_POINT_ALREADY_MEMBER

CERTIFIED_IN_EXO_FOUNDATIONS = 'EXO_FOUNDATIONS'
CERTIFIED_IN_EXO_ATTRIBUTES = 'EXO_ATTRIBUTES'
CERTIFIED_IN_EXO_COACH = 'EXO_COACH'

CERTIFICATION_LEAD_EXO_FOUNDATIONS = 'EXO_FOUNDATIONS'
CERTIFICATION_LEAD_EXO_ATTRIBUTES = 'EXO_ATTRIBUTES'
CERTIFICATION_LEAD_EXO_COACH = 'EXO_COACH'

CERTIFICATION_TYPE_FOUNDATIONS = 'ExO Advisor'
CERTIFICATION_CORRELATION = {
    CERTIFICATION_TYPE_FOUNDATIONS: CERTIFIED_IN_EXO_FOUNDATIONS,
}


class HubSpotException(Exception):
    pass


class HubSpotUserDoesNotExistException(HubSpotException):
    pass


class ContactEncoder(json.JSONEncoder):
    def default(self, o):
        data = {'properties': []}
        for key, value in o.__dict__.items():
            if value is None:
                continue
            if key == 'onboarding_entry_point':
                if value == ON_BOARDING_ENTRY_POINT_CERTIFIED:
                    data['properties'].append(
                        {
                            'property': 'certification_leads',
                            'value': CERTIFICATION_LEAD_EXO_FOUNDATIONS,
                        }
                    )
                elif value == ON_BOARDING_ENTRY_POINT_SUMMITS:
                    data['properties'].append(
                        {
                            'property': 'preferred_city_summit',
                            'value': o.summit_city,
                        }
                    )
            data['properties'].append(
                {
                    'property': key,
                    'value': value,
                }
            )

        return data


class Contact:
    full_name = None
    email = None
    interested_joining_the_community = ''
    onboarding_entry_point = None
    summit_city = None
    community_life_cycle = None
    _vid = None
    _hubspot_data = {}
    _user = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '{} - {}'.format(self.full_name, self.email)

    @property
    def vid(self):
        if not self._vid:
            self._request_hubspot_contact()

        return self._vid

    @property
    def user_community_life_cycle(self):
        user_community_life_cycle = COMMUNITY_LIFE_CYCLE_LEAD
        if not self._user:
            self._user = get_user_model().objects.get(email=self.email)

        if hasattr(self._user, 'consultant') and self._user.consultant.is_active:
            user_community_life_cycle = COMMUNITY_LIFE_CYCLE_MEMBER

        return user_community_life_cycle

    def get_url(self, operation):
        return '{}/{}/{}/'.format(URL_BASE, CONTACT_SECTION, operation)

    def build_params(self, **kwargs):
        params = kwargs.copy()
        params['hapikey'] = settings.HAPIKEY
        return params

    def _set_hubspot_property(self, hubspot_property, property_value, raise_exception=True):
        try:
            data = json.dumps({
                'properties': [
                    {
                        'property': hubspot_property,
                        'value': property_value,
                    }
                ]
            })
            response = requests.post(
                self.get_url('contact/email/{}/profile'.format(self.email)),
                params=self.build_params(),
                data=data
            )
            assert status.is_success(response.status_code)
            logger.info(
                'Setting property [{}:{}] to contact: {} OK'.format(
                    hubspot_property,
                    property_value,
                    self.email,
                )
            )

        except AssertionError:
            logger.error(
                'Exception setting property [{}:{}] to contact: {} - Request status code [{}]'.format(
                    hubspot_property,
                    property_value,
                    self.email,
                    response.status_code,
                )
            )
            if raise_exception:
                raise HubSpotException(
                    'Cannot set property {} to user {} - Response[{}]'.format(
                        hubspot_property,
                        self.email,
                        response.status_code,
                    )
                )

    def get_hubspot_property(self, property_name):
        if not self._hubspot_data:
            self._request_hubspot_contact()

        return self._hubspot_data.get(
            'properties'
        ).get(property_name, {}).get('value', '')

    def update_property(self, property_name, property_value):
        self._set_hubspot_property(property_name, property_value)

    def update_email(self, new_email):
        self._set_hubspot_property('email', new_email)

    def set_certification(self, certification_name):
        self._set_hubspot_property('certified_in', CERTIFICATION_CORRELATION.get(certification_name))

    def convert_contact_to_member(self):
        self._set_hubspot_property('community_life_cycle', COMMUNITY_LIFE_CYCLE_MEMBER)

    def set_foundations_joining_date(self, date):
        timestamp = int(date.timestamp()) * 1000
        self.update_property('foundations_signup_date', timestamp)

    def update_or_create_contact(self):
        try:
            self._request_hubspot_contact()
            self.update_property('interested_joining_the_community', self.interested_joining_the_community)
            self.update_property('community_life_cycle', self.user_community_life_cycle)
            if not self.get_hubspot_property('onboarding_entry_point'):
                self.update_property('onboarding_entry_point', self.onboarding_entry_point)
        except HubSpotUserDoesNotExistException:
            self.create_contact()

    def create_contact(self):
        self.community_life_cycle = COMMUNITY_LIFE_CYCLE_LEAD

        try:
            data = json.dumps(self, cls=ContactEncoder)
            response = requests.post(
                self.get_url('contact'),
                params=self.build_params(),
                data=data,
            )
            assert response.status_code in [requests.codes.ok, requests.codes.conflict]

            if response.status_code == requests.codes.conflict:
                self._set_hubspot_property('community_life_cycle', COMMUNITY_LIFE_CYCLE_LEAD)

        except AssertionError:
            logger.error(
                'create_contact - Exception creating a new contact: {}'.format(
                    response.content
                )
            )

    def _request_hubspot_contact(self):
        hubspot_api_url = self.get_url('contact/email')

        url = '{}{}/profile?hapikey={}'.format(
            hubspot_api_url,
            self.email,
            settings.HAPIKEY,
        )

        response = requests.get(url)
        if status.is_success(response.status_code):
            self._hubspot_data = response.json()
            self._vid = response.json().get('vid')
            self.full_name = self.get_hubspot_property('full_name')

        elif status.is_client_error(response.status_code):
            raise HubSpotUserDoesNotExistException(
                'User with email {} does not exist at HubSpot'.format(self.email)
            )

    @classmethod
    def get_contact(cls, email):
        hubspot_contact = cls(email=email)
        try:
            hubspot_contact._request_hubspot_contact()
            return hubspot_contact
        except HubSpotException as e:
            del hubspot_contact
            raise e

    @classmethod
    def read_contact(cls, hubspot_node):
        email = None
        fullname = None
        for identity in hubspot_node['identity-profiles'][0]['identities']:
            if identity['type'] == 'EMAIL':
                email = identity['value']
        node_fullname = hubspot_node['properties'].get('full_name')
        fullname = fullname.get('value') if node_fullname else ''
        return cls(email=email, full_name=fullname)
