from django.views.generic.edit import FormView
from django.contrib.admin import helpers
from django.conf import settings

from ..forms import UploadForm
from ..models import Resource
from ..clients import FileStackClient


def upload_file(file_io):
    client = FileStackClient()
    filelink = client.upload(file_obj=file_io)
    metadata = filelink.metadata()

    defaults = {
        'link': filelink.url,
        'url': filelink.url,
        'type': settings.RESOURCE_CH_TYPE_FILESTACK,
        'status': settings.RESOURCE_CH_STATUS_AVAILABLE,
        'sections': [],
        'extra_data': metadata
    }

    resource, _ = Resource.objects.get_or_create(
        name=file_io.name)
    resource.__dict__.update(**defaults)
    resource.save()
    return resource


class UploadFileView(FormView):
    template_name = 'upload_form.html'
    form_class = UploadForm
    success_url = ''

    def get_adminform(self):
        adminForm = helpers.AdminForm(
            self.form_class,
            [(None, {'fields': [*self.form_class.base_fields]})],
            {},
            [],
            model_admin=self)
        return adminForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['opts'] = Resource._meta
        context['add'] = True
        context['change'] = False
        context['is_popup'] = False
        context['save_as'] = False
        context['has_add_permission'] = True
        context['has_change_permission'] = True
        context['has_view_permission'] = True
        context['has_delete_permission'] = False
        context['has_editable_inline_admin_formsets'] = False
        context['show_save_and_continue'] = False
        context['title'] = 'Upload file to Filestack'
        context['has_file_field'] = True
        context['adminform'] = self.get_adminform()
        context['resource'] = getattr(self, 'resource', None)
        return context

    def form_valid(self, form):
        self.resource = None
        self.resource = upload_file(form.files['file'])
        return self.get(self.request)
