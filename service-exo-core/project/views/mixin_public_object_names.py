
class PublicObjectNamesMixin:

    def get_subobject(self):
        if hasattr(self, 'get_object'):
            object = self.get_object()
            return object.real_type

        return None

    def _get_object(self):
        obj = None
        if hasattr(self, 'get_object'):
            obj = self.get_subobject()
        elif hasattr(self, 'model'):
            obj = self.model
        elif hasattr(self, 'project'):
            obj = self.project

        return obj

    def get_public_object_name(self):
        public_object_name = self._get_object()
        if public_object_name:
            return public_object_name._meta.verbose_name
        else:
            return None

    def get_public_object_name_plural(self):
        public_object_name_plural = self._get_object()
        if public_object_name_plural:
            return public_object_name_plural._meta.verbose_name_plural
        else:
            return None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['type_project'] = self.get_public_object_name()
        context['type_project_plural'] = self.get_public_object_name_plural()

        return context
