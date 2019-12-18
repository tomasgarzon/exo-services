from django.db import models
from django.conf import settings
from django.db.models import Q


class MemberQueryset(models.QuerySet):

    def filter_active(self):
        return self.filter(
            user__consultant__status=settings.CONSULTANT_STATUS_CH_ACTIVE
        )

    def filter_inactive(self):
        return self.exclude(
            user__consultant__status=settings.CONSULTANT_STATUS_CH_ACTIVE
        )

    def filter_by_industries(self, industries):
        query = Q()
        for item in industries:
            query |= Q(user__consultant__industries__industry__name=item)

        return self.filter(query).distinct()

    def filter_by_attributes(self, attributes):
        query = Q()
        for item in attributes:
            query |= Q(
                user__consultant__exo_attributes__level__gt=0,
                user__consultant__exo_attributes__exo_attribute__name=item)

        return self.filter(query).distinct()

    def filter_by_certifications(self, certifications):
        query = Q()
        for item in certifications:
            query |= Q(
                user__consultant__consultant_roles__certification_role__code=item)
        return self.filter(query).distinct()

    def filter_by_roles(self, roles):
        query = Q()
        for item in roles:
            query |= Q(
                user__consultant__roles__exo_role__code=item,
                user__consultant__roles__visible=True)

        return self.filter(query).distinct()

    def filter_by_activities(self, activities):
        query = Q()
        for item in activities:
            query |= Q(user__consultant__exo_profile__exo_activities__exo_activity__code=item)

        return self.filter(query).distinct()

    def filter_by_technologies(self, technologies):
        query = Q()
        for item in technologies:
            query |= Q(user__consultant__keywords__keyword__name=item)

        return self.filter(query).distinct()

    def filter_by_languages(self, languages):
        query = Q()
        for item in languages:
            query |= Q(user__consultant__languages__name=item)

        return self.filter(query).distinct()

    def filter_by_location(self, location):
        query = Q()
        for item in location:
            query |= Q(user__location__icontains=item)

        return self.filter(query).distinct()

    def search(self, pattern):
        return self.filter(user__full_name__icontains=pattern)

    def filter_for_public(self):
        return self.filter_by_certifications([
            settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
            settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH,
        ]).filter(
            user__consultant__status=settings.CONSULTANT_STATUS_CH_ACTIVE
        )
