from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ReferralRewardAcquiredMailView(BaseMailView):
    template_name = 'mails/referrals/referral_reward_acquired.html'
    mandatory_mail_args = [
        'reward_name',
        'reward_description',
        'user_email',
        'user_full_name',
    ]
    optional_mail_args = []
    subject = _('New referral reward')
    section = 'referrals'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'user_full_name': faker.name(),
            'user_email': faker.email(),
            'reward_name': '[reward name]',
            'reward_description': '[reward description]',
        })
        return mock_data
