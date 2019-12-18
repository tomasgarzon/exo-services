from django.db.models import Q


def get_fields():
    return [
        {'instance_name': 'full_name', 'label': 'Name'},
        {'instance_name': 'email', 'label': 'e-mail'},
        {'instance_name': 'location', 'label': 'Location'},
        {'instance_name': 'status', 'label': 'Status'}
    ]


def get_value(item, field):
    field_name = field.get('instance_name')
    value = None
    if field_name == 'extended_bio':
        value = item.user.bio_me
    elif field_name == 'bio':
        value = item.user.about_me
    elif field_name == 'languages':
        value = [language.name for language in item.languages.all()]

    if value and isinstance(value, list):
        value = ', '.join(value)

    return value


def get_filtered_data(queryset, pattern, order_by=None):
    if pattern:
        filter_by_name = Q(user__full_name__icontains=pattern)
        filter_by_email = Q(user__email__icontains=pattern)
        filter_by_location = Q(user__location__icontains=pattern)
        queryset = queryset.filter(
            filter_by_name | filter_by_email | filter_by_location
        )

    # Order data
    direction = 1
    ordering = 'user__full_name'
    allowed_order = {
        'full_name': 'user__full_name',
        'email': 'user__email',
        'location': 'user__location',
        'status': 'status',
    }

    if order_by:
        if order_by[0] == '-':
            direction = -1
            order_by = order_by[1:]

        if order_by in allowed_order.keys():
            ordering = allowed_order.get(order_by)

        if direction < 0:
            ordering = '-{}'.format(ordering)

    return queryset.order_by(ordering)
