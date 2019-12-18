from django.db.models import QuerySet


class SurveyQueryset(QuerySet):

    def filter_by_user(self, user):
        return self.filter(created_by=user)
