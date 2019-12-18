from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from .mixin import OpportunityMailMixin


class Create(OpportunityMailMixin):

    def get_data(self):
        data = super().get_data()
        user_wrapper = UserWrapper(user=self.opportunity.created_by)
        data.update({
            'created_by_profile_picture': user_wrapper.get_profile_picture(settings.LARGE_IMAGE_SIZE),
            'created_by_name': user_wrapper.full_name,
            'created_by_role': user_wrapper.user_title,
            'public_url': self.opportunity.url_public,
            'budget_string': self.opportunity.budget_string,
            'num_positions': self.opportunity.num_positions,
            'description': self.opportunity.description,
            'entity_name': self.opportunity.entity,
            'location_string': self.opportunity.location_string,
            'start_date': self.opportunity.start_date.strftime('%d %b, %Y') if self.opportunity.start_date else '',
            'duration': self.opportunity.duration,
            'tags': list(self.opportunity.keywords.all().values_list(
                'name', flat=True)),
            'reply_to': [
                user_wrapper.email,
            ],
        })
        return data


class CreateWithoutAgreementSigned:

    def __init__(self, opportunity, user):
        self.opportunity = opportunity
        self.user_recipient = user

    def get_data(self):
        user_wrapper = UserWrapper(user=self.opportunity.created_by)

        return {
            'title': self.opportunity.title,
            'created_by_profile_picture': user_wrapper.get_profile_picture(settings.MEDIUM_IMAGE_SIZE),
            'created_by_name': user_wrapper.get_full_name(),
            'created_by_user_title': user_wrapper.user_title,
            'recipient_name': self.user_recipient.get('full_name'),
            'public_url': self.opportunity.url_public,
            'role': self.opportunity.role_string,
            'disable_notification_url': self.user_recipient.get('disable_notification_url'),
        }
