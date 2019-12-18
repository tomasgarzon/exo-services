from django.conf import settings
from django.contrib.auth import get_user_model

from ...signals_define import (
    opportunity_post_send, opportunity_send_to_user,
    opportunity_post_rejected)


User = get_user_model()


class OpportunityTaggedMixin:

    def _add_user_tagged(self, user_uuid, notification=True):
        user = User.objects.get(uuid=user_uuid)
        self.users_tagged.create(user=user)
        if notification:
            opportunity_send_to_user.send(
                sender=self.__class__, opportunity=self,
                user=user,
            )

    def _remove_user_tagged(self, user_uuid):
        user = User.objects.get(uuid=user_uuid)
        user_tagged = self.users_tagged.filter(user=user).first()
        applicant = user_tagged.applicant
        user_tagged.delete()
        if applicant:
            self._remove_applicant(applicant)

    def _remove_applicant(self, applicant):
        opportunity_post_rejected.send(
            sender=applicant.__class__,
            opportunity=self,
            applicant=applicant,
        )
        applicant.delete()

    def from_open_to_tagged(self, users):
        self.set_target(settings.OPPORTUNITIES_CH_TARGET_FIXED)
        for user_uuid in users:
            self._add_user_tagged(user_uuid, notification=False)

        for applicant_info in self.applicants_info.exclude(user__uuid__in=users):
            self._remove_applicant(applicant_info)

    def from_tagged_to_open(self):
        self.set_target(settings.OPPORTUNITIES_CH_TARGET_OPEN)
        self.users_tagged.all().delete()
        self.sent_at = None
        self.save()
        opportunity_post_send.send(
            sender=self.__class__, opportunity=self,
        )

    def tagged_changed_users(self, previous_users, new_users):
        users_to_remove = previous_users - new_users
        for user_uuid in users_to_remove:
            self._remove_user_tagged(user_uuid)

        users_to_add = new_users - previous_users
        for user_uuid in users_to_add:
            self._add_user_tagged(user_uuid)

    def update_target_and_users(self, target_change, users_tagged_change):
        new_target, previous_target = target_change
        new_users, previous_users = users_tagged_change

        target_changed = new_target != previous_target
        users_changed = set(new_users) != set(previous_users)

        open_not_changed = not target_changed and self.is_opened
        tagged_not_changed = not users_changed and self.is_tagged and not target_changed
        if open_not_changed or tagged_not_changed:
            return

        if target_changed:
            if self.is_opened:
                self.from_open_to_tagged(new_users)
            else:
                self.from_tagged_to_open()
        elif users_changed:
            self.tagged_changed_users(
                previous_users=set(previous_users),
                new_users=set(new_users))
