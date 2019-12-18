import django_filters

from ..models import Invitation


class InvitationFilter(django_filters.FilterSet):

    class Meta:
        model = Invitation
        fields = ['hash']

    @property
    def qs(self):
        hash_value = self.data.get('hash', '')
        if not hash_value:
            self.queryset = self._meta.model.objects.none()
        else:
            self.queryset = self._meta.model.objects.all()
        return super().qs
