from django.db import models


class DeletedControlMixin(models.Model):

    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        if not self.deleted:
            self.deleted = True
            self.save(update_fields=['deleted', ])

    def force_delete(self, using=None, keep_parents=False):
        return super().delete(using, keep_parents)
