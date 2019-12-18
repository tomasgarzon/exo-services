from django.conf import settings


def get_role_names(role_list):
    return list(role_list.values_list('name', flat=True))


def calculate_user_position(user):
    user_positions = []
    roles = []
    if user.organizations_roles.exists():
        roles = user.organizations_roles.filter(
            status=settings.RELATION_ROLE_CH_ACTIVE
        ).order_by('position')

    if roles:
        for position, org_name in roles.values_list('position', 'organization__name'):
            user_positions.append('{} at {}'.format(position, org_name))

    return ', '.join(user_positions)


def calculate_user_title(user):
    user_position = calculate_user_position(user)
    user_titles = []
    if user_position:
        user_titles += user_position.split(',')

    if user.is_consultant:
        certified_roles = user.consultant.certification_roles.all()

        user_titles += get_role_names(certified_roles)

    return ', '.join(user_titles)
