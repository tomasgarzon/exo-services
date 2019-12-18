from django.db import models


class EventQuerySet(models.QuerySet):

    def filter_by_category(self, category):
        return self.filter(category__code=category)

    def filter_by_status(self, status):
        return self.filter(_status=status)

    def filter_by_user(self, user):
        queryset = None
        if user.is_superuser:
            queryset = self.all()
        else:
            user_is_participant = models.Q(participants__user=user)
            user_is_owner = models.Q(created_by=user)
            queryset = self.filter(user_is_owner | user_is_participant)
        return queryset
