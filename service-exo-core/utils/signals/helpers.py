DEFAULT_UPDATE_FIELDS = ['status', 'modified']


def is_instance_status_updated(object, update_fields=[]):

    return set(DEFAULT_UPDATE_FIELDS) == set(update_fields)
