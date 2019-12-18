from django import template

from ..helpers import UserProfileWrapper

register = template.Library()


@register.simple_tag
def user_profile_url(user):
    return UserProfileWrapper(user).profile_slug_url
