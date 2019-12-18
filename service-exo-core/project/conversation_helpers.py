from django.conf import settings

from custom_auth.helpers import UserProfileWrapper

from .user_title_helpers import get_user_title_in_project


ICON_FILESTACK_URL = {
    'coaches': 'https://cdn.filestackcontent.com/N4Ggba1IRUGib03DvTBE',
    'all_members': 'https://cdn.filestackcontent.com/VaLQ6i8SlaHZh9MBVLbA',
    'T_0': 'https://cdn.filestackcontent.com/kpRzP37Tw6Hdp2iqinjw',
    'T_1': 'https://cdn.filestackcontent.com/4J7o0xYFSXK6bODeKgli',
    'T_2': 'https://cdn.filestackcontent.com/qlFWPUyjQxC6fNF4rZRU',
    'S_0': 'https://cdn.filestackcontent.com/zmVW1DkCRzuWwYMWSO9Y',
    'S_1': 'https://cdn.filestackcontent.com/vTk5DILsRimLEH8G1foW',
    'S_2': 'https://cdn.filestackcontent.com/yiz0S1aSqmrzpvz9Vky9',
}


def add_user(user, project):
    return {
        'name': user.get_full_name(),
        'profile_picture': user.profile_picture.get_thumbnail_url(48, 48),
        'short_title': get_user_title_in_project(project, user),
        'profile_url': UserProfileWrapper(user).profile_slug_url,
        'user_uuid': str(user.uuid),
    }


def create_conversation_groups(project):
    groups = [
        {
            'name': 'All Members',
            'users': [],
            'icon': ICON_FILESTACK_URL['all_members']
        },
        {
            'name': 'Coaches',
            'users': [],
            'icon': ICON_FILESTACK_URL['coaches']
        },
    ]
    teams = {
        'S': 0,
        'T': 0
    }

    for team in project.teams.all():
        group_team = {'name': team.name, 'users': [], 'icon': ''}

        for user in team.team_members.all():
            user_team = add_user(user, project)
            group_team['users'].append(user_team)
            groups[0]['users'].append(user_team)

        icon_name = '{}_{}'.format(team.stream, teams[team.stream] % 3)
        group_team['icon'] = ICON_FILESTACK_URL.get(icon_name)
        teams[team.stream] += 1
        user_coach = add_user(team.coach.user, project)
        group_team['users'].append(user_coach)
        groups.append(group_team)
        groups[1]['users'].append(user_coach)
        groups[0]['users'].append(user_coach)

    for user in project.consultants_roles.filter_by_exo_role_code(
            settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH).consultants().users():

        user_manager = add_user(user, project)

        for group in groups:
            group['users'].append(user_manager)

    return groups
