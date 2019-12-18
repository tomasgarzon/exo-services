from autoslug import AutoSlugField

from ..signals import edit_slug_field


class TagAutoSlugField(AutoSlugField):

    def __init__(self, *args, **kwargs):
        self._tag_model = kwargs.pop('tag_model', None)
        super().__init__(*args, **kwargs)

    def pre_save(self, instance, add):
        assert self._tag_model
        previous_value = None
        if not add:
            previous_value = getattr(instance, self.name)
        slug = super(TagAutoSlugField, self).pre_save(instance, add)
        if previous_value and previous_value != slug:
            edit_slug_field.send(
                sender=self.__class__,
                instance=instance,
                previous_value=previous_value,
                new_value=slug,
                tag_model=self._tag_model,
            )
        return slug


class AutoSlugCustomManagerField(AutoSlugField):

    def pre_save(self, instance, add):
        self.manager = instance.__class__.slug_manager
        return super().pre_save(instance, add)
