from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper


class OpportunityMailMixin:

    def __init__(self, opportunity):
        self.opportunity = opportunity

    def get_data(self):
        user_wrapper = UserWrapper(user=self.opportunity.created_by)

        return {
            'title': self.opportunity.title,
            'created_by_profile_picture': user_wrapper.get_profile_picture(settings.MEDIUM_IMAGE_SIZE),
            'created_by_name': user_wrapper.get_full_name(),
            'created_by_role': user_wrapper.user_title,
            'role': self.opportunity.role_string,
            'category_code': self.opportunity.category.code,
        }
