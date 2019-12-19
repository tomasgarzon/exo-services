from rest_framework import serializers
from django.utils.encoding import smart_text
from django.contrib.auth import get_user_model


class UserUUIDRelatedField(serializers.SlugRelatedField):

    def to_internal_value(self, data):
        user = self.get_queryset().filter(**{self.slug_field: data}).first()
        if user is None:
            user = get_user_model().objects.retrieve_remote_user_by_uuid(data)
            if user.is_anonymous:
                self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
        return user
