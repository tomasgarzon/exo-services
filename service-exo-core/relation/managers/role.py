from django.db import models
from django.db.utils import IntegrityError


class RoleManager(models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def actives(self):
        return self.get_queryset().actives_only()

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def only_visible(self):
        return self.get_queryset().only_visible()

    def check_validation(self, user, role):
        args = self.get_args_for_create(user, role)
        return self.get_queryset().filter(**args).count() == 0

    def get_args_for_create(self, user, role):
        return {}

    def get_or_create_role(self, user, role, status=None):
        # Avoid duplicated roles
        valid = self.check_validation(user, role)
        if not valid:
            args = self.get_args_for_create(user, role)
            return self.get_queryset().get(**args), False
        else:
            try:
                return self.create_role(user, role, status), True
            except IntegrityError:
                args = self.get_args_for_create(user, role)
                return self.get_queryset().get(**args), False

    def create_role(self, user, role, status=None):
        args = self.get_args_for_create(user, role)
        if status:
            args.update({'status': status})
        new_role = self.create(**args)
        return new_role
