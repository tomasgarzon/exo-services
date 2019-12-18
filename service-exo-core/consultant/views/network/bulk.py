import codecs

from django.conf import settings
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from achievement.models import Achievement

from ...models import (
    BulkCreationConsultant, Consultant
)
from ...forms import BulkCreationConsultantForm
from .helpers import read_name_email_coins_from_csv


class BulkCreationConsultantFormView(
        PermissionRequiredMixin,
        CreateView
):
    template_name = 'network/bulk_creation_form.html'
    permission_required = settings.CONSULTANT_FULL_PERMS_ADD_CONSULTANT
    model = BulkCreationConsultant
    form_class = BulkCreationConsultantForm
    raise_exception = True

    def get_success_message(self, *args, **kwargs):
        bulk_creation = kwargs.get('bulk_creation')
        return '{} invitations created successfully'.format(bulk_creation.consultants.success().count())

    def get_success_url(self, bulk_creation):
        return reverse('consultant:bulk-add-detail', kwargs={'pk': bulk_creation.pk})

    def create_bulk_creation(self, form):
        bulk_creation = form.save()
        bulk_creation.created_by = self.request.user
        bulk_creation.save()
        return bulk_creation

    def create_bulk_user(self, new_user, bulk_creation):
        return BulkCreationConsultant.objects.create(
            name=new_user.name,
            email=new_user.email,
            coins=new_user.coins,
            bulk_creation=bulk_creation,
        )

    def invite_consultant(self, new_user, custom_message):
        short_name = new_user.name.split(' ')[0]
        consultant = Consultant.objects.create_consultant(
            short_name=short_name,
            full_name=new_user.name,
            email=new_user.email,
            invite_user=self.request.user,
            registration_process=True,
            custom_text=custom_message,
            coins=new_user.coins,
        )
        return consultant

    def update_existing_user(self, new_user, bulk_creation_consultant):
        if not new_user.user.is_consultant:
            bulk_creation_consultant.set_error_email_used()
        else:
            consultant = new_user.user.consultant
            if not new_user.has_coins:
                bulk_creation_consultant.set_error_email_used()
            elif new_user.has_achievement_created():
                bulk_creation_consultant.set_error_achievement_created()
            else:
                Achievement.objects.create_reward_for_consultant(
                    consultant,
                    new_user.coins,
                )
            bulk_creation_consultant.set_consultant(consultant)

    def form_valid(self, form):
        bulk_creation = self.create_bulk_creation(form)

        filecontent = form.cleaned_data.get('file_csv')
        filecontent = codecs.iterdecode(filecontent, 'utf-8')
        users_list = read_name_email_coins_from_csv(filecontent)
        for new_user in users_list:
            bulk_creation_consultant = self.create_bulk_user(new_user, bulk_creation)
            if new_user.missing_information():
                bulk_creation_consultant.set_error_missing_information()
            elif new_user.exists:
                self.update_existing_user(new_user, bulk_creation_consultant)
            else:
                consultant = self.invite_consultant(
                    new_user, form.cleaned_data.get('custom_text'),
                )
                bulk_creation_consultant.set_consultant(consultant)
        success_message = self.get_success_message(**{'bulk_creation': bulk_creation})
        messages.success(self.request, success_message)
        return HttpResponseRedirect(self.get_success_url(bulk_creation))
