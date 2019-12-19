from ..func_utils import infer_method_name
from .exceptions import CustomFilterDescriptorError


class CustomFilterDescriptor:

    FILTER_METHOD_NAME = 'filter_by'

    def __init__(self, field_name, field_value_filter):
        self.field_name = field_name
        self.field_value_filter = field_value_filter

    def __get__(self, obj, objtype):

        def get_custom_filter():
            method_name = infer_method_name(
                self.field_name,
                self.FILTER_METHOD_NAME,
            )

            try:
                class_method = getattr(obj, method_name)
                return class_method(self.field_value_filter)
            except AttributeError:
                raise NotImplementedError(
                    'Class `{}` does not implement `{}`'.format(
                        obj.__class__.__name__, method_name,
                    ),
                )

        return get_custom_filter


class CustomFilterDescriptorMixin:
    """
    For every field and option in FILTER_DESCRIPTORS dict
    in the super class this descriptor build
    "filter_by_[field]_[option]" and
    call to method filter_by_[field] of the super class
    with the current option for filter

    """
    FILTER_PREFIX = 'filter_by'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices_list = self.get_choices()

        for choice_value in choices_list:
            field_name = choice_value.get('field')
            options = choice_value.get('options')

            for choice_code, method_name in options:
                self.set_descriptor(choice_code, method_name, field_name)

    def get_choices(self):
        try:
            choices = self.FILTER_DESCRIPTORS
        except AttributeError:
            raise CustomFilterDescriptorError(
                'FILTER_DESCRIPTORS dict not defined',
            )

        return choices

    def set_descriptor(self, choice_code, method_name, field_name):
        format_method_name = infer_method_name(method_name)
        format_descriptor = infer_method_name(
            field_name,
            self.FILTER_PREFIX,
            '_{}'.format(format_method_name),
        )

        setattr(
            self.__class__,
            format_descriptor,
            CustomFilterDescriptor(field_name, choice_code),
        )
