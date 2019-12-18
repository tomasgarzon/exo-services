import datetime

from django.conf import settings


def normalize_deal_name(level, contact, date=None, lang=None):
    if not date:
        name = '{} {}'.format(level, contact)
    else:
        name = '{} ({} {}) {}'.format(level, date.strftime('%h'), lang, contact)

    return name


def datetime_to_hubspot_timestamp(date_time):
    date = date_time.replace(hour=0, minute=0, second=0)
    return int(date.timestamp()) * 1000


def hubspot_timestamp_to_date(timestamp):
    return datetime.date.fromtimestamp(int(timestamp) / 1000)


def get_entry_point_by_level(level):
    return settings.EXO_CERTIFICATION_LEVELS_EP_MAPPING.get(level, '')
