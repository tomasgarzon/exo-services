from django.utils import six
from django.forms.models import ModelFormMetaclass, BaseModelForm
from django.forms.forms import BaseForm, DeclarativeFieldsMetaclass


class PlaceholderMixin():
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        meta = getattr(new_class, 'Meta', None)
        if meta and getattr(meta, 'placeholders', None) and new_class.base_fields:
            for field, placeholder in meta.placeholders.items():
                if hasattr(new_class.base_fields[field], 'choices'):
                    new_class.base_fields[field].widget.attrs.update(
                        {'data-placeholder': placeholder},
                    )
                new_class.base_fields[field].widget.attrs.update(
                    {'placeholder': placeholder},
                )
        return new_class


class CustomModelFormMetaclass(PlaceholderMixin, ModelFormMetaclass):
    pass


class CustomModelForm(six.with_metaclass(
    CustomModelFormMetaclass,
    BaseModelForm,
)):
    pass


class CustomFormMetaclass(PlaceholderMixin, DeclarativeFieldsMetaclass):
    pass


class CustomForm(six.with_metaclass(
    CustomFormMetaclass,
    BaseForm,
)):
    pass
