from auth_uuid.utils.user_wrapper import UserWrapper
from utils.collections import StatusString

from ...signals_define import opportunity_status_changed
from ...conf import settings


class OpportunityUserStatusMixin:

    @property
    def admin_users(self):
        users = [self.created_by]
        if self.group is not None:
            users.extend(list(self.group.managers.all()))
        return users

    @property
    def previous_status(self):
        try:
            return self.history.order_by('-created')[1]._status
        except IndexError:
            return None

    def has_cancelations(self, user_from):
        return self.cancelations.filter_by_user(user_from).count()

    def user_status_for_applicant(self, user_from):
        applicant = self.applicants_info.get(user=user_from)
        return applicant.status

    def is_applicant(self, user_from):
        return self.get_applicants_for_user(user_from).exists()

    def get_applicants_for_user(self, user_from):
        return self.applicants_info.filter_by_user(user=user_from)

    def get_status_display(self):
        return self.get__status_display()

    @property
    def status(self):
        return StatusString(
            self._status, choices=settings.OPPORTUNITIES_CH_STATUS,
        )

    @status.setter
    def status(self, user_status):
        try:
            user_from, new_status = user_status
        except ValueError:
            raise ValueError('User or new status missing')

        is_same_status = self._status == new_status
        is_same_user_last_update = self.last_user_modification == user_from
        if is_same_status and is_same_user_last_update:
            return

        previous_status = self._status
        self._status = new_status
        self.save(update_fields=['_status', 'modified'])
        self.history.create(
            status=new_status,
            user=user_from)

        opportunity_status_changed.send(
            sender=self.__class__,
            request=self,
            status=new_status,
            previous_status=previous_status)

    @property
    def last_user_modification(self):
        return self.last_history.user

    @property
    def last_history(self):
        return self.history.latest('created')

    @property
    def requested_by(self):
        return self.history.filter(status=settings.OPPORTUNITIES_CH_REQUESTED).first()

    @property
    def user_created_by(self):
        return self.history.filter(status=settings.OPPORTUNITIES_CH_DRAFT).first()

    @property
    def selected_by(self):
        return set([app.selected_by for app in self.applicants_selected])

    @property
    def closed_by(self):
        return self.history.filter(status=settings.OPPORTUNITIES_CH_CLOSED).first()

    def get_history(self, status):
        return self.history.filter(status=status).last()

    def user_status(self, user_from):
        user_wrapper = UserWrapper(user=user_from)
        user_is_consultant_and_can_apply = user_wrapper.is_consultant

        if self.is_applicant(user_from):
            return self.user_status_for_applicant(user_from)
        elif self.is_opened and user_is_consultant_and_can_apply:
            return settings.OPPORTUNITIES_CH_APPLICANT_DRAFT

        return self._status

    def user_actions(self, user_from, remove_admin_actions=False):
        actions = []
        user_wrapper = UserWrapper(user=user_from)

        user_with_actions = user_wrapper.is_consultant \
            or user_wrapper.is_superuser \
            or user_wrapper.is_delivery_manager \
            or user_from in self.admin_users

        if not user_with_actions:
            return actions

        admin_perms = user_from.is_superuser or\
            user_wrapper.is_delivery_manager or\
            user_from in self.admin_users

        if self.is_draft and admin_perms:
            actions.extend(settings.OPPORTUNITIES_ACTION_CH_SEND)
        elif self.is_requested:
            can_apply = self.can_apply(user_from, raise_exception=False)
            if can_apply:
                actions.extend(settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN)

            if admin_perms:
                actions.extend(settings.OPPORTUNITIES_ACTION_CH_EDIT)
                actions.extend(settings.OPPORTUNITIES_ACTION_CH_CLOSE)
                actions.extend(settings.OPPORTUNITIES_ACTION_CH_REMOVE)
        elif self.is_closed:
            if admin_perms:
                actions.extend(settings.OPPORTUNITIES_ACTION_CH_RE_OPEN)
        if remove_admin_actions:
            actions = list(set(actions) - set(settings.OPPORTUNITIES_ADMIN_ACTIONS))

        return actions
