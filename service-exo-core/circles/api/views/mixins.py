from actstream.models import Follow

from django.db.models import F, Q, Func, Value
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from rest_framework import filters, generics, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.compat import distinct
from exo_role.api.serializers import CertificationRoleSerializer

from consultant.models import Consultant
from forum.api.serializers.author import ForumAuthorSerializer
from forum.permission_helpers import user_in_circle
from utils.http_response_mixin import HttpResponseMixin
from ...models import Circle
from ...exceptions import CircleRemovedException, CirclePermissionException


class BasicPageNumberPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'


class CustomSearchFilter(filters.SearchFilter):

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)

        if not search_terms:
            return queryset
        base = queryset
        q1 = Q(short_name_joined__istartswith=search_terms[0])
        q2 = Q(full_name_joined__istartswith=search_terms[0])
        queryset = queryset.annotate(
            short_name_joined=Func(
                F('short_name'),
                Value(' '), Value(''),
                function='replace'),
            full_name_joined=Func(
                F('full_name'),
                Value(' '), Value(''),
                function='replace')
        ).filter(q1 | q2)
        queryset = distinct(queryset, base)
        return queryset


class CirclesDispatchAPIViewMixin(HttpResponseMixin):

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except exceptions.ValidationError:
            exc = exceptions.PermissionDenied()
            response = self.handle_exception(exc)
            self.response = self.finalize_response(request, response, *args, **kwargs)
            return self.response
        except CircleRemovedException as err:
            return self.gone_410_response(
                classname=err.circle.__class__.__name__,
                object_id=err.circle.pk)
        except CirclePermissionException as err:
            return self.forbidden_403_response(
                classname=err.circle.__class__.__name__,
                name=err.circle.name,
                slug=err.circle.slug,
                type=err.circle.type,
                image=err.circle.image,
                description=err.circle.description,
                certificationRequired=CertificationRoleSerializer(err.circle.certification_required).data
            )

    def check_circle_is_removed(self, circle):
        if circle and circle.removed:
            raise CircleRemovedException(circle, 'Circle removed')

    def check_user_is_follower(self, user, circle):
        user = self.request.user

        if circle and not user_in_circle(user, circle):
            raise CirclePermissionException(circle, 'Circle permission')


class FollowerListMixin(CirclesDispatchAPIViewMixin, generics.ListAPIView):
    model = get_user_model()
    renderer_classes = (CamelCaseJSONRenderer,)
    filter_backends = (CustomSearchFilter,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ForumAuthorSerializer

    def get_queryset(self):
        circle_slug = self.kwargs.get('slug', None)
        circle = None

        if circle_slug:
            circle = Circle.all_objects.filter(slug=circle_slug).first()

        if circle:
            self.check_circle_is_removed(circle)
            self.check_user_is_follower(self.request.user, circle)
            followers = Follow.objects.followers_qs(circle).values('user')
            queryset = get_user_model().objects.filter(id__in=followers)
        elif circle_slug == settings.CIRCLES_QUESTIONS_PROJECTS_SLUG:
            queryset = Consultant.objects.filter_consulting_enabled().users()
        elif circle_slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
            queryset = Consultant.objects.all().users()
        else:
            raise Http404

        return queryset.order_by('short_name')
