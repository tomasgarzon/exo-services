from django.core.exceptions import ObjectDoesNotExist

from ..conf import settings


class AgreementMixin():
    """
    Mixing for models that are realted with an Agreement
    """

    @property
    def agreements(self):
        """
        Return the user collection Agreements in order to make possible to
        creaque queries over itself
        """
        return self.user.agreements

    @property
    def last_agreement(self):
        try:
            return self.agreements.all().latest('created')
        except ObjectDoesNotExist:
            return None

    @property
    def agreement(self):
        """
        Return the Signed Agreement for this user if exist
        NOTE:
        We should determine the type of recipient to this kind
        of queries [agreement__recipient] for now always is
        a Consultant Type
        """
        try:
            return self.agreements.filter_by_status_accepted().filter(
                agreement__status=settings.AGREEMENT_STATUS_ACTIVE,
                agreement__recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
            ).latest('agreement__version')
        except ObjectDoesNotExist:
            return None

    @property
    def active_agreements(self):
        return self.agreements.filter_by_status_accepted()

    @property
    def revoked_agreements(self):
        return self.agreements.filter_by_status_revoked()

    @property
    def pending_agreements(self):
        return self.agreements.filter_by_status_pending()

    def add_user_agreement(self):
        # Add last agreement for consultant
        return self.agreements.create_user_agreement(
            settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )
