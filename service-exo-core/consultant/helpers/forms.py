from django.forms import ModelChoiceField, ModelMultipleChoiceField


class ConsultantChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.user.get_full_name()


class ConsultantMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.user.get_full_name()
