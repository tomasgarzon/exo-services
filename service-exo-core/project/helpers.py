from django.conf import settings
from django.contrib.auth import get_user_model

from permissions.shortcuts import has_project_perms


def next_project_url(project, user):
    zone = False
    is_a_participant = user.projects_member \
        .filter_by_project(project) \
        .exclude_staff_and_admin() \
        .actives_only() \
        .exists()

    is_a_coach = user.is_consultant and user.consultant.teams_coach.filter_by_project(project).exists()
    project_admin = has_project_perms(
        project,
        settings.PROJECT_PERMS_PROJECT_MANAGER,
        user,
    )

    if is_a_participant or is_a_coach:
        url = project.get_frontend_index_url(user)
        if url and url.startswith('http'):
            zone = True
    elif user.is_superuser or project_admin:
        url = project.get_absolute_url()
        zone = True
    else:
        consultant_project_roles = project.consultants_roles.filter_by_user(user)
        is_manager = False
        can_access_to_project = False

        for c_project_role in consultant_project_roles:
            if c_project_role.has_manager_perms:
                is_manager = True
            elif c_project_role.exo_role.code == settings.EXO_ROLE_CODE_SPRINT_REPORTER:
                can_access_to_project = True

        if is_manager:
            url = project.get_absolute_url()
            zone = True
        elif can_access_to_project:
            url = project.get_frontend_index_url(user)
        else:
            url = ''
    return url, zone


def get_feedback_from_objects(team_step, objects):
    results = []
    sum_rate = 0
    sum_feelings = 0
    sum_comments = 0
    average_rate = 0
    average_feeling = 0
    total_reviews = 0
    total_reviewers = objects.count()

    for user in objects:
        comment = None
        rate = team_step.get_rating_for_user(user)
        feeling = team_step.get_feedback_for_user(user)

        if rate and feeling:
            total_reviews += 1
            sum_rate += rate
            sum_feelings += feeling

            last_feedback_action = team_step.get_last_action_feedback(
                user=user,
                verb=settings.TEAM_ACTION_COMMENT_WEEKLY)

            if last_feedback_action and last_feedback_action.description:
                sum_comments += 1
                comment = {
                    'text': last_feedback_action.description,
                    'date': last_feedback_action.timestamp,
                }

            result = {
                'fullName': user.full_name,
                'thumbnail': user.profile_picture.url,
                'feeling': team_step.get_feedback_for_user(user),
                'rate': team_step.get_rating_for_user(user),
                'comment': comment,
            }

            results.append(result)

    if total_reviews:
        average_rate = round(sum_rate / total_reviews, 1)
        average_feeling = round(sum_feelings / total_reviews, 0)

    data = {
        'average_rate': average_rate,
        'average_feelings': average_feeling,
        'total_reviewers': total_reviewers,
        'total_comments': sum_comments,
        'results': results,
    }

    return data


def get_feedback_summary(user_from, team_step):
    summary = []
    team = team_step.team
    step = team_step.step
    project = step.project
    is_user_team_coach = user_from == team.coach.user

    try:
        is_user_head_coach = user_from == project.project_manager.user
    except AttributeError:
        is_user_head_coach = False
    is_user_delivery_manager = user_from.has_perm(
        settings.PROJECT_PERMS_DELIVERY_MANAGER, team_step.project)

    if is_user_team_coach:
        # Coach
        # see team results

        team_members = team.team_members.all()

        data = get_feedback_from_objects(team_step, team_members)
        data['origin'] = settings.PROJECT_STEP_FEEDBACK_FROM_TEAM_MEMBERS
        summary.append(data)

    elif is_user_head_coach or is_user_delivery_manager:
        # Head Coach and Delivery manager
        # see team results and coach results

        team_coachs = get_user_model().objects.filter(pk=team.coach.user.pk)

        data = get_feedback_from_objects(team_step, team_coachs)
        data['origin'] = settings.PROJECT_STEP_FEEDBACK_FROM_COACH
        summary.append(data)

        team_members = team.team_members.all()

        data = get_feedback_from_objects(team_step, team_members)
        data['origin'] = settings.PROJECT_STEP_FEEDBACK_FROM_TEAM_MEMBERS
        summary.append(data)

    return summary
