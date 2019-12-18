from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from consultant.models import Consultant
from forum.models import Post

from .models import Circle


def get_question_projects_circle():
    circle = Circle()
    circle.name = settings.CIRCLES_QUESTIONS_PROJECTS_NAME
    circle.slug = settings.CIRCLES_QUESTIONS_PROJECTS_SLUG
    circle.image = settings.CIRCLES_QUESTIONS_PROJECTS_IMAGE
    circle.description = settings.CIRCLES_QUESTIONS_PROJECTS_DESCRIPTION
    circle.total_posts = Post.objects.filter_by__type_project().count()
    return circle


def get_announcements_circle():
    circle = Circle()
    circle.name = settings.CIRCLES_ANNOUNCEMENT_NAME
    circle.slug = settings.CIRCLES_ANNOUNCEMENT_SLUG
    circle.image = settings.CIRCLES_ANNOUNCEMENT_IMAGE
    circle.description = settings.CIRCLES_ANNOUNCEMENT_DESCRIPTION
    circle.total_posts = Post.objects.filter_by__type_announcement().count()
    return circle


def get_circle_total_members(circle):
    if circle.slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
        is_superuser = Q(is_active=True, is_superuser=True)
        active_consultant = Q(
            consultant__pk__in=Consultant.objects.all().values_list('pk', flat=True))
        return get_user_model().objects.filter(
            active_consultant | is_superuser
        ).count()
    elif circle.slug == settings.CIRCLES_QUESTIONS_PROJECTS_SLUG:
        return get_user_model().objects.filter(
            consultant__consultant_roles__certification_role__code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS
        ).count()
    else:
        return circle.total_members


def get_circle_tags(circle):
    virtual_circles = [
        settings.CIRCLES_ANNOUNCEMENT_SLUG,
        settings.CIRCLES_QUESTIONS_PROJECTS_SLUG,
    ]
    if circle.slug in virtual_circles:
        return []
    else:
        return circle.tags


def get_circle_last_questions(circle, limit=3):
    if circle.slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
        queryset = Post.objects.filter_by__type(
            post_type=settings.FORUM_CH_ANNOUNCEMENT)
    elif circle.slug == settings.CIRCLES_QUESTIONS_PROJECTS_SLUG:
        queryset = Post.objects.filter_by__type(
            post_type=settings.FORUM_CH_PROJECT)
    else:
        queryset = Post.objects.filter_by_circle(circle)
    return queryset.order_by('-modified')[0:limit]


def get_circle_edit_permissions(circle, user_from):
    virtual_circles = [
        settings.CIRCLES_ANNOUNCEMENT_SLUG,
        settings.CIRCLES_QUESTIONS_PROJECTS_SLUG,
    ]
    if circle.slug in virtual_circles:
        return False
    else:
        return circle.can_edit(user_from, False)


def get_circle_leave_permissions(circle, user_from):
    virtual_circles = [
        settings.CIRCLES_ANNOUNCEMENT_SLUG,
        settings.CIRCLES_QUESTIONS_PROJECTS_SLUG,
    ]
    if circle.slug in virtual_circles:
        return False
    else:
        return circle.user_can_leave(user_from, False)


def get_circle_post_permissions(circle, user_from):
    if circle.slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
        return user_from.is_staff
    elif circle.slug == settings.CIRCLES_QUESTIONS_PROJECTS_SLUG:
        return False
    else:
        return circle.check_user_can_post(user_from, False)


def get_circle_user_status(circle, user_from):
    if circle.slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
        return True
    elif circle.slug == settings.CIRCLES_QUESTIONS_PROJECTS_SLUG:
        return False
    else:
        return circle.user_status(user_from)
