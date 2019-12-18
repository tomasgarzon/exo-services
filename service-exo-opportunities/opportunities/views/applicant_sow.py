from __future__ import absolute_import

from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.core.exceptions import PermissionDenied

from wkhtmltopdf.views import PDFTemplateView

from ..models import Applicant


class ApplicantSowPDF(
        LoginRequiredMixin,
        SingleObjectMixin, PDFTemplateView):
    template_name = 'applicant_sow.html'
    model = Applicant
    context_object_name = 'applicant'
    raise_exception = True

    @property
    def filename(self):
        return 'applicant_sow_{}.pdf'.format(self.object.pk)

    def check_permissions(self, user, applicant):
        is_superuser = user.is_superuser
        is_owner = applicant.user == user
        is_requester = applicant.opportunity.created_by == user
        try:
            assert is_superuser or is_owner or is_requester
        except AssertionError:
            raise PermissionDenied()

    def get(self, request, pk):
        self.object = self.get_object()
        self.check_permissions(request.user, self.object)
        if not self.object.has_sow:
            raise Http404
        return super().get(request, pk)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['sow'] = self.object.sow
        return context
