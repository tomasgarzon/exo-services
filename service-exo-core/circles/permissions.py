from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import BasePermission

from consultant.models import Consultant

from .models import Circle
from .conf import settings


class CanViewCircle(BasePermission):

    def has_permission(self, request, view):
        can_view = False
        circle_name = view.kwargs.get('name')
        try:
            circle = Circle.objects.get(
                name__iexact=circle_name)
            can_view = circle.is_user_in_followers(request.user)
        except Circle.DoesNotExist:
            if circle_name == settings.CIRCLES_PROJECT_QUESTION_CIRCLE_NAME:
                can_view = request.user in Consultant.objects.filter_consulting_enabled().users()
            else:
                raise ObjectDoesNotExist

        return can_view or request.user.is_superuser
