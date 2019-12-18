import requests
import logging

from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

URL_CONTRACTING_DATA = '/api/accounts/user/{}/contracting-data/'
logger = logging.getLogger('service')


def get_contracting_data(user):
    data = {}
    url = URL_CONTRACTING_DATA.format(user.uuid.__str__())
    url = '{}{}'.format(
        settings.EXOLEVER_HOST,
        url)
    logger.info('Calling to contracting data')
    if settings.POPULATOR_MODE:
        return {}
    try:
        response = requests.get(
            url,
            headers={'USERNAME': settings.AUTH_SECRET_KEY})
    except Exception as err:
        message = 'requests.Exception: {}'.format(err)
        logger.error(message)
        response = None
        raise err

    if response and response.status_code == requests.codes.ok:
        response_data = response.json()
        if not response_data.get('name'):
            response_data['name'] = UserWrapper(user=user).get_full_name()
        data = response_data.copy()
    return data


def fill_applicant_data(user):
    data = {'applicant_name': ''}
    contracting_data = get_contracting_data(user)
    data['applicant_name'] = contracting_data.get('name', None)
    return data


def fill_requester_data(user):
    data = {'requester_name': ''}
    contracting_data = get_contracting_data(user)
    data['requester_name'] = contracting_data.pop('name', None)
    data.update(contracting_data)
    return data


def init_sow_from_applicant(applicant):
    fields_from_opportunity = [
        'title', 'description', 'mode',
        'location', 'place_id', 'location_url',
        'exo_role', 'certification_required',
        'entity', 'budgets',
        'start_date', 'end_date', 'other_role_name',
        'duration_unity', 'duration_value',
    ]
    data = {}

    for field in fields_from_opportunity:
        data[field] = getattr(applicant.opportunity, field)

    data.update(fill_applicant_data(applicant.user))
    data.update(fill_requester_data(applicant.opportunity.created_by))
    return data
