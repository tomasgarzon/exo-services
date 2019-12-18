from django.contrib.auth import get_user_model

from survey.models import Survey

from populate.populator.builder import Builder


User = get_user_model()


class SurveyBuilder(Builder):

    def create_object(self):
        created_by = self.data.get('created_by')
        return Survey.objects.create(
            created_by=created_by,
            name=self.data.get('name'),
            slug=self.data.get('slug'),
            send_results=self.data.get('send_results'),
            show_results=self.data.get('show_results'))
