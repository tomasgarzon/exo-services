import csv

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse

from ..models import ConsultantRoleCertificationGroup
from ..forms.certification_group_search import (
    CertificationGropuSearchListForm,
    CreateCertificationGroup,
    UpdateCertificationGroup)


class CertificationGroupListView(
        PermissionRequiredMixin,
        ListView):

    model = ConsultantRoleCertificationGroup
    template_name = 'certification_group/list.html'
    filter_form_class = CertificationGropuSearchListForm
    paginate_by = 50
    permission_required = 'relation.list_consultantrolecertificationgroup'

    def get(self, request, *args, **kwargs):
        self.form_filter = self.filter_form_class(request.GET)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all().order_by('-issued_on')
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        if data.get('search'):
            q1 = Q(name__icontains=data.get('search'))
            queryset = queryset.filter(q1)
        if data.get('issued_on'):
            q2 = Q(issued_on=data.get('issued_on'))
            queryset = queryset.filter(q2)
        return queryset.distinct()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_filter'] = self.form_filter
        return context


class CertificationGroupCreateView(CreateView):
    model = ConsultantRoleCertificationGroup
    template_name = 'certification_group/create.html'
    form_class = CreateCertificationGroup

    def get_form_kwargs(self, *args, **kwargs):
        response = super().get_form_kwargs(*args, **kwargs)
        response['user'] = self.request.user
        return response

    def get_success_url(self):
        return reverse('tools:relation:group-list')


class CertificationGroupUpdateView(UpdateView):
    model = ConsultantRoleCertificationGroup
    template_name = 'certification_group/update.html'
    form_class = UpdateCertificationGroup

    def get_form_kwargs(self, *args, **kwargs):
        response = super().get_form_kwargs(*args, **kwargs)
        response['user'] = self.request.user
        return response

    def get_success_url(self):
        return reverse('tools:relation:group-list')


class CertificationGroupDetailView(DetailView):
    model = ConsultantRoleCertificationGroup
    template_name = 'certification_group/detail.html'


class CertificationGroupExportAsCSVView(DetailView):
    model = ConsultantRoleCertificationGroup

    def get(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        header = [
            'Name', 'email', 'Issued on',
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="consultant.csv"'
        writer = csv.writer(response)
        writer.writerow(header)
        for item in instance.consultant_roles.all():
            row = [
                item.consultant.user.get_full_name(),
                item.consultant.user.email,
                item.credentials.first().issued_on.strftime('%Y-%m-%d') if item.credentials.first().issued_on else '',
            ]
            writer.writerow(row)

        return response
