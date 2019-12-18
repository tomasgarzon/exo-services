from .group_names import GROUP_NAMES


class GroupName():

    @classmethod
    def build_name(cls, key_name, **kwargs):
        return GROUP_NAMES.get(key_name).format(**kwargs)
