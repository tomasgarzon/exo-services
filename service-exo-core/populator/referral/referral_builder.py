from django.conf import settings

from populate.populator.builder import Builder

from referral.models import Campaign


class ReferralBuilder(Builder):

    def create_object(self):
        campaign, _ = Campaign.objects.get_or_create(
            name=self.data.get('name'),
            campaign_id=self.data.get('campaign_id'),
            status=self.data.get('status', settings.REFERRAL_CAMPAIGN_STATUS_DEFAULT),
        )

        for user_data in self.data.get('users'):
            user = user_data.get('user')
            token = user_data.get('token')
            campaign.users.add(user)
            subscriber = campaign.subscriber_set.get(user=user)
            subscriber.token = token
            subscriber.save(update_fields=['token'])

        return campaign
