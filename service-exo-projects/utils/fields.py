from multiselectfield import MultiSelectField


# Multiselect field to Django 2.X
class PatchedMultiSelectField(MultiSelectField):

    def value_to_string(self, obj):
        # value = self._get_val_from_obj(obj)
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
