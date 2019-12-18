from .consultant_validation_status import ConsultantValidationStatus


class ConsultantValidationMixin():

    validation_name = ''

    @property
    def consultant_validation_status(self):
        if hasattr(self, 'consultant_id'):
            consultant_id = self.consultant_id
        else:
            if hasattr(self.user, 'consultant'):
                consultant_id = self.user.consultant.id
        try:
            return ConsultantValidationStatus.objects.get(
                consultant__id=consultant_id,
                validation__name=self.validation_name,
            )
        except ConsultantValidationStatus.DoesNotExist:
            return None
