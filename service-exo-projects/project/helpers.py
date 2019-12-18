from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper


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

            user_wrapper = UserWrapper(user=user)
            result = {
                'fullName': user_wrapper.get_full_name(),
                'thumbnail': user_wrapper.profile_picture_96,
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
    is_user_team_admin = team.user_is_admin(user_from)
    is_user_project_admin = project.user_is_admin(user_from)

    if is_user_team_admin:
        team_members = team.participants

        data = get_feedback_from_objects(team_step, team_members)
        data['origin'] = settings.PROJECT_STEP_FEEDBACK_FROM_TEAM_MEMBERS
        summary.append(data)

    elif is_user_project_admin:

        team_coachs = team.coaches

        data = get_feedback_from_objects(team_step, team_coachs)
        data['origin'] = settings.PROJECT_STEP_FEEDBACK_FROM_COACH
        summary.append(data)

        team_members = team.participants

        data = get_feedback_from_objects(team_step, team_members)
        data['origin'] = settings.PROJECT_STEP_FEEDBACK_FROM_TEAM_MEMBERS
        summary.append(data)

    return summary
