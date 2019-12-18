from ..external_groups import get_users_in_group


class EmailMixin:

    def get_group_destinataries(self, group_name):
        return get_users_in_group(group_name)
