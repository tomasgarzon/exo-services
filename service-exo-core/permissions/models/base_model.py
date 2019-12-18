from model_utils.models import TimeStampedModel


class BasePermissionsModel(TimeStampedModel):
    def __init__(self, *args, **kwargs):
        self._meta_permissions = self.MetaPermissions()
        super().__init__(*args, **kwargs)

    class Meta:
        abstract = True
