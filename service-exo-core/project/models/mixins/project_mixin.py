from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model

from exo_role.models import ExORole

from permissions.shortcuts import has_project_perms
from consultant.models import Consultant


class ProjectCreationMixin:

    def can_add_service(self, user_from):
        perms_for_creating = user_from.has_perm(settings.PROJECT_ADD_PROJECT)
        is_consultant = user_from.is_consultant

        if not perms_for_creating and not is_consultant:
            raise ValidationError('User {} has no perms to add service'.format(user_from))

    def can_add_service_sprint_automated(self, user_from):
        if not user_from.has_perm(settings.SPRINT_AUTOMATED_FULL_ADD_SPRINT):
            raise ValidationError('User {} has no perms to add service'.format(user_from))


class ProjectUpdateMixin:
    edit_permission = settings.PROJECT_PERMS_EDIT_PROJECT

    def check_edit_perms(self, user_from):
        if not has_project_perms(self, self.edit_permission, user_from):
            raise ValidationError('No permissions to edit project')

    def get_or_create_consultant(self, user_from, consultant, exo_role, status=None):
        if self.role_is_manager(exo_role) or not self.is_draft:
            status = settings.RELATION_ROLE_CH_ACTIVE
        else:
            status = settings.RELATION_ROLE_CH_INACTIVE

        return self.consultants_roles.get_or_create_consultant(
            user_from=user_from,
            consultant=consultant,
            project=self,
            exo_role=exo_role,
            status=status,
        )

    def get_or_create_user(self, user_from, name, email):
        new_member, created = get_user_model().objects.get_or_create(
            email=email,
            send_notification=False,
            user_from=user_from,
            autosend=False,
            invitation_status=settings.INVITATION_STATUS_CH_ACTIVE,
            defaults={
                'full_name': name,
                'short_name': name.split(' ')[0]
            },
        )

        if not created and not new_member.is_active:
            new_member.is_active = True
            new_member.save(update_fields=['is_active'])

        return new_member

    def update(self, user_from, name, customer, start, consultants=None, customer_members=None):
        self.check_edit_perms(user_from)
        self.name = name
        self.customer = customer
        self.start = start
        self.save(update_fields=['name', 'customer', 'start'])

        if consultants is not None:
            self.update_consultants(user_from, consultants)

        if customer_members is not None:
            self.update_members(user_from, customer_members)

        return self

    def update_consultants(self, user_from, consultants):
        """
            consultants: format( {'email': '...', 'exo_role': '...'})
        """
        self.check_edit_perms(user_from)

        previous_consultants = set(self.consultants_roles.values_list('consultant', 'exo_role'))

        consultants_added = []

        for item in consultants:

            consultant = Consultant.all_objects.get(user__email=item.get('email'))
            self.get_or_create_consultant(user_from, consultant, item.get('exo_role'))
            consultants_added.append((consultant.id, item.get('exo_role').pk))

        for consultant_id, exo_role in previous_consultants - set(consultants_added):
            consultant = Consultant.objects.get(id=consultant_id)

            try:
                consultant_role = self.consultants_roles._get_consultant(
                    consultant=consultant,
                    project=self,
                    exo_role=exo_role,
                )
                consultant_role.delete()

            except self.consultants_roles.model.DoesNotExist:
                continue

    def update_members(self, user_from, customer_members):
        self.check_edit_perms(user_from)

        previous_members = set(self.users_roles.all().values_list('user__email', flat=True))
        new_mails = []

        for member in customer_members:
            new_mails.append(member.get('email'))

            if not self.get_member(email=member.get('email')):
                self.add_user_project_member(
                    user_from=user_from,
                    email=member.get('email'),
                    name=member.get('short_name') or member.get('name'),
                )
            new_mails.append(member.get('email'))

        for old_member in previous_members - set(new_mails):
            self.remove_user_project_member(user_from, old_member)

    def add_user_project_member(self, user_from, name, email):
        new_user = self.get_or_create_user(user_from, name, email)
        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)

        self.users_roles.get_or_create_user(
            user_from=user_from,
            user=new_user,
            project=self,
            exo_role=exo_role)
        return new_user

    def add_user_project_supervisor(self, user_from, name, email):
        new_user = self.get_or_create_user(user_from, name, email)
        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_OBSERVER)

        self.users_roles.get_or_create_user(
            user_from=user_from,
            user=new_user,
            project=self,
            exo_role=exo_role)
        return new_user

    def add_user_project_staff(self, user_from, name, email):
        new_user = self.get_or_create_user(user_from, name, email)
        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_OTHER)

        self.users_roles.get_or_create_user(
            user_from=user_from,
            user=new_user,
            project=self,
            exo_role=exo_role)
        return new_user

    def add_user_project_delivery_manager(self, user_from, name, email):
        new_user = self.get_or_create_user(user_from, name, email)
        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_DELIVERY_MANAGER)

        self.users_roles.get_or_create_user(
            user_from=user_from,
            user=new_user,
            project=self,
            exo_role=exo_role)
        return new_user

    def remove_user_project_member(self, user_from, email):
        self.check_edit_perms(user_from)
        user_project_role = self.get_member(email)
        return self.users_roles.remove_user(user_project_role.user, user_project_role.exo_role)

    def remove_user_project_supervisor(self, user_from, email):
        self.check_edit_perms(user_from)
        user_project_role = self.get_member(email)
        return self.users_roles.remove_user(user_project_role.user, user_project_role.exo_role)

    def get_member(self, email):
        return self.users_roles.filter(user__email=email).first()
