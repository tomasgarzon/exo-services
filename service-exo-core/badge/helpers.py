from django.conf import settings

from .models import Badge, UserBadgeActivity, UserBadgeJob


FASTRACK = 'fastracksprint'
WORKSHOP = 'workshop'


def add_user_badge_items(user_badge, items):
    for item in items:
        user_badge.user_badge_items.update_or_create(
            name=item.get('name'),
            defaults={
                'date': item.get('date')
            })


def delete_user_badge_items(user_badge, items):
    for item in items:
        user_badge.user_badge_items.filter(
            name=item.get('name')).delete()

    if not user_badge.user_badge_items.count():
        user_badge.delete()


def update_or_create_badge(
    user_from,
    user_to,
    code,
    category,
    num=1,
    description='',
    items=[],
    delete=False,
):

    user_badge = None
    badges = Badge.objects.filter(code=code, category=category)

    if badges.exists():
        badge = badges.first()
        badges_user = user_to \
            .get_badges(code=badge.code) \
            .filter(badge__category=category)

        # UPDATE
        if badges_user.exists():
            user_badge = badges_user.first()
            log_verb = settings.BADGE_ACTION_LOG_UPDATE

            # Only JOB badges need action here
            # Activity badges only apply 1 time
            if len(items):
                if delete:
                    log_verb = settings.BADGE_ACTION_LOG_DELETE
                    delete_user_badge_items(user_badge, items)
                else:
                    add_user_badge_items(user_badge, items)

        # CREATE
        else:
            log_verb = settings.BADGE_ACTION_LOG_CREATE

            if len(items):
                user_badge_child = UserBadgeJob.objects.create(
                    badge=badge,
                    user=user_to)

                add_user_badge_items(user_badge_child.userbadge_ptr, items)

            else:
                user_badge_child = UserBadgeActivity.objects.create(
                    badge=badge,
                    user=user_to)

            user_badge = user_badge_child.userbadge_ptr

        user_badge.create_log(
            user_from=user_from,
            verb=log_verb,
            description=description,
        )

    return user_badge
