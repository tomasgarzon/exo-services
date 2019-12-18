import tempfile

from django import forms
from django.core.management import call_command

from exo_role.models import CertificationRole
from exo_certification.management.commands.create_certificates import Command
from consultant.models import Consultant
from utils.forms.form_placeholder import CustomForm, CustomModelForm
from ..models import ConsultantRoleCertificationGroup


class CertificationGropuSearchListForm(CustomForm):

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input form-control'}),
    )
    issued_on = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input form-control'}),
    )

    class Meta:
        placeholders = {
            'search': 'Search by name',
            'issued_on': 'yyyy-mm-dd'
        }


CH_NAME = (
    ('ExO Ambassador', 'ExO Ambassador'),
    ('ExO Consultant', 'ExO Consultant'),
    ('ExO Sprint Coach', 'ExO Sprint Coach'),
    ('ExO Trainer', 'ExO Trainer'),
    ('ExO Foundations', 'ExO Foundations'),
    ('ExO Board Advisor', 'ExO Board Advisor'),
)

GROUP_TYPE = (
    ('consultantrole-ambassador', 'ExO Ambassador'),
    ('consultantrole-consultant', 'ExO Consultant'),
    ('consultantrole-sprint-coach', 'ExO Sprint Coach'),
    ('consultantrole-exo-trainer', 'ExO Trainer'),
    ('consultantrole-foundations', 'ExO Foundations'),
    ('consultantrole-board-advisor', 'ExO Board Advisor'),
)


class CreateCertificationGroup(CustomModelForm):
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
    )
    course_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'input form-control'}),
    )
    type = forms.ChoiceField(
        required=True,
        label='Type',
        choices=GROUP_TYPE,
        widget=forms.Select(
            attrs={'class': 'select2'},
        ),
    )
    course_name = forms.ChoiceField(
        required=True,
        label='Name',
        choices=CH_NAME,
        widget=forms.Select(
            attrs={'class': 'select2'},
        ))
    issued_on = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'input form-control'}),
    )

    class Meta:
        model = ConsultantRoleCertificationGroup
        fields = [
            'name', 'description', 'issued_on',
        ]
        placeholders = {
            'name': 'ExO {Ambassador | Consultant | Sprint Coach | Trainer | Foundations | Board Advisor} Certification - {Virtual | City}}',  # noqa
            'course_name': 'ExO {Ambassador | Consultant | Sprint Coach | Trainer | Foundations | Board Advisor}',
            'content': 'email1\nemail2\nemail3',
            'issued_on': 'yyyy-mm-dd',
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        role_type = cleaned_data.get('type')
        role_code = Command().get_role_code(role_type)
        certification_role = CertificationRole.objects.get(code=role_code)

        for email in content.splitlines():
            try:
                consultant = Consultant.objects.get(
                    user__emailaddress__email=email)
            except Consultant.DoesNotExist:
                msg = 'Consultant does not exist: {}'.format(email)
                self.add_error('content', msg)
                consultant = None
            if consultant and consultant.consultant_roles.filter(
                    certification_role=certification_role,
                    credentials__isnull=False).exists():
                msg = 'Consultant already certified: {}'.format(email)
                self.add_error('content', msg)
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        fake_namefile = tempfile.NamedTemporaryFile()
        with open(fake_namefile.name, 'w') as fake_csv:
            fake_csv.write(cleaned_data.get('content'))
        call_command(
            'create_certificates',
            '--name', cleaned_data.get('name'),
            '--course_name', cleaned_data.get('course_name'),
            '--description', cleaned_data.get('description'),
            '--user_from', self.user.email,
            '--issued_on', cleaned_data.get('issued_on').strftime('%Y-%m-%d'),
            '--type', cleaned_data.get('type'),
            '--file', fake_namefile.name)


class UpdateCertificationGroup(CustomModelForm):
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = ConsultantRoleCertificationGroup
        fields = ['description']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        certification_role = self.instance.consultant_roles.first().certification_role

        for email in content.splitlines():
            try:
                consultant = Consultant.objects.get(
                    user__emailaddress__email=email)
            except Consultant.DoesNotExist:
                msg = 'Consultant does not exist: {}'.format(email)
                self.add_error('content', msg)
                consultant = None
            if consultant and consultant.consultant_roles.filter(
                    certification_role=certification_role,
                    credentials__isnull=False).exists():
                msg = 'Consultant already certified: {}'.format(email)
                self.add_error('content', msg)
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        fake_namefile = tempfile.NamedTemporaryFile()
        with open(fake_namefile.name, 'w') as fake_csv:
            fake_csv.write(cleaned_data.get('content'))
        call_command(
            'update_certificates',
            '--name', self.instance.name,
            '--when', self.instance.issued_on.strftime('%Y-%m-%d'),
            '--file', fake_namefile.name)
