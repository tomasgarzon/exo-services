from django.utils.text import slugify

from ..func_utils import infer_method_name


class ChoicesDescriptor:

    def __init__(self, choice_code, choice_value):
        self.choice_code = choice_code
        self.choice_value = choice_value

    def __get__(self, obj, objtype):
        return self.choice_code == getattr(obj, self.choice_value)


class ChoicesDescriptorMixin:
    DESCRIPTOR_FORMAT_DEFAULT = 'is'
    CHOICES_FIELDS_DEFAULT = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices_list = self.get_choices()

        for choice_value in choices_list:

            options = self.get_options_from_field(choice_value)

            for choice_code, method_name in options:
                self.set_descriptor(
                    choice_code,
                    slugify(method_name).replace('-', '_'), choice_value)

    def get_choices(self):
        try:
            choices = self.CHOICES_DESCRIPTOR_FIELDS
        except AttributeError:
            choices = self.CHOICES_FIELDS_DEFAULT

        return choices

    def get_options_from_field(self, field_name):
        options = None
        try:
            index = self.CHOICES_DESCRIPTOR_FIELDS.index(field_name)
            options = self.CHOICES_DESCRIPTOR_FIELDS_CHOICES[index]
        except (AttributeError, ValueError, IndexError):
            pass
        if not options:
            try:
                # Django models
                options = self._meta.get_field(field_name).get_choices()
            except AttributeError:
                # Mongo models
                options = self._fields.get(field_name).choices

        return options

    def set_descriptor(self, choice_code, method_name, choice_value):
        setattr(
            self.__class__,
            infer_method_name(
                method_name,
                self.DESCRIPTOR_FORMAT_DEFAULT,
            ),
            ChoicesDescriptor(choice_code, choice_value),
        )
