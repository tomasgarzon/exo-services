from django.contrib.auth.models import Group


class EmailMixin:

    def get_group_destinataries(self, group_name):
        group, created = Group.objects.get_or_create(name=group_name)
        return list(group.user_set.values_list('email', flat=True))
