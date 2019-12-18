from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from exo_role.models import ExORole, CertificationRole
from relation.models import ConsultantRole, ConsultantProjectRole, UserProjectRole


ROLES_MAPPING = {
    # Project roles
    settings.ROL_CH_HEAD_COACH: settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
    settings.ROL_CH_COACH: settings.EXO_ROLE_CODE_SPRINT_COACH,
    settings.ROL_CH_SPEAKER: settings.EXO_ROLE_CODE_AWAKE_SPEAKER,
    settings.ROL_CH_COLLABORATOR: settings.EXO_ROLE_CODE_ADVISOR,
    settings.ROL_CH_SWARM_ADVISOR: settings.EXO_ROLE_CODE_ADVISOR,
    settings.ROL_CH_DISRUPTOR: settings.EXO_ROLE_CODE_DISRUPTOR,
    settings.ROL_CH_DISRUPTOR_SPEAKER: settings.EXO_ROLE_CODE_DISRUPTOR_SPEAKER,
    settings.ROL_CH_SPRINT_ADMIN: settings.EXO_ROLE_CODE_DELIVERY_MANAGER,
    settings.ROL_CH_SPRINT_CONTRIBUTOR: settings.EXO_ROLE_CODE_SPRINT_CONTRIBUTOR,
    settings.ROL_CH_ALIGN_TRAINER: settings.EXO_ROLE_CODE_ALIGN_TRAINER,
    settings.ROL_CH_REPORTER: settings.EXO_ROLE_CODE_SPRINT_REPORTER,
    settings.ROL_CH_PROJECT_DIRECTOR: settings.EXO_ROLE_CODE_SPRINT_OTHER,
    settings.ROL_CH_LEARNING_DESIGNER: settings.EXO_ROLE_CODE_SPRINT_OTHER,
    # Project roles with no badges
    settings.ROL_CH_USER_MEMBER_REGULAR: settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
    settings.ROL_CH_USER_MEMBER_SUPERVISOR: settings.EXO_ROLE_CODE_SPRINT_OBSERVER,
    settings.ROL_CH_USER_MEMBER_DELIVERY_MANAGER: settings.EXO_ROLE_CODE_DELIVERY_MANAGER,
    settings.ROL_CH_USER_MEMBER_STAFF: settings.EXO_ROLE_CODE_SPRINT_OTHER,
    # Fastrack roles
    settings.ROL_CH_TEAM_LEADER: settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER,
    settings.ROL_CH_TEAM_MEMBER: settings.EXO_ROLE_CODE_FASTRACK_TEAM_MEMBER,
    settings.ROL_CH_CURATOR: settings.EXO_ROLE_CODE_FASTRACK_CURATOR,
    settings.ROL_CH_CO_CURATOR: settings.EXO_ROLE_CODE_FASTRACK_CO_CURATOR,
    settings.ROL_CH_SOLUTION_ACCELERATOR: settings.EXO_ROLE_CODE_FASTRACK_SOLUTION_ACCELERATOR,
    settings.ROL_CH_OBSERVER: settings.EXO_ROLE_CODE_FASTRACK_OBSERVER_EVALUATOR,
    settings.ROL_CH_LOCAL_TEAM_MEMBER: settings.EXO_ROLE_CODE_FASTRACK_LOCAL_TEAM_MEMBER,
    # Workshops roles
    settings.ROL_CH_TRAINER: settings.EXO_ROLE_CODE_WORKSHOP_TRAINER,
    settings.ROL_CH_SPEAKER_WORKSHOP: settings.EXO_ROLE_CODE_WORKSHOP_SPEAKER,
    # Others roles
    settings.ROL_CH_ACCOUNT_MANAGER: settings.EXO_ROLE_CODE_ACCOUNT_MANAGER,
}

CERTS_ROLES_MAPPING = {
    settings.ROL_CH_AMBASSADOR: settings.EXO_ROLE_CODE_CERTIFICATION_AMBASSADOR,
    settings.ROL_CH_CONSULTANT: settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
    settings.ROL_CH_COACH: settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH,
    settings.ROL_CH_EXO_TRAINER: settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER,
    settings.ROL_CH_EXO_FOUNDATIONS: settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS,
    settings.ROL_CH_BOARD_ADVISOR: settings.EXO_ROLE_CODE_CERTIFICATION_BOARD_ADVISOR,
}


class Command(BaseCommand):

    def get_exo_role(self, old_code):
        exo_role = None
        new_code = ROLES_MAPPING.get(old_code)

        if new_code:
            exo_role = ExORole.objects.get(code=new_code)

        return exo_role

    def get_certification_role(self, old_code):
        exo_role = None
        new_code = CERTS_ROLES_MAPPING.get(old_code)

        if new_code:
            exo_role = CertificationRole.objects.get(code=new_code)

        return exo_role

    def migrate_consultant_roles(self):
        self.stdout.write(self.style.WARNING('ConsultantRole migration ...'))

        for consultant_role in ConsultantRole.objects.filter(role__isnull=False):
            new_role = self.get_certification_role(consultant_role.role.code)

            if new_role:
                consultant_role.certification_role = new_role
                consultant_role.save(update_fields=['certification_role'])

        self.stdout.write(self.style.SUCCESS('ConsultantRole migrated'))

    def migrate_consultant_roles_trainers(self):
        self.stdout.write(self.style.WARNING('ConsultantRole trainers migration ...'))

        roles = [
            settings.ROL_CH_TRAINER,
            settings.ROL_CH_ALIGN_TRAINER,
        ]

        for consultant_role_for_delete in ConsultantRole.objects.filter(role__code__in=roles):

            try:
                consultant_role_for_delete_parent = consultant_role_for_delete.consultant.consultant_roles.get(
                    certification_role__code=settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER)

                credential = consultant_role_for_delete.credentials.all().first()

                if credential:
                    credential.object_id = consultant_role_for_delete_parent.pk
                    credential.save()

                consultant_role_for_delete.delete()
            except ObjectDoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS('ConsultantRole trainers migrated'))

    def migrate_consultant_project_roles(self):
        self.stdout.write(self.style.WARNING('ConsultantProjectRole migration ...'))

        for consultant_project_role in ConsultantProjectRole.objects.filter(role__isnull=False):
            old_role = consultant_project_role.role
            new_role = self.get_exo_role(old_role.code)

            if new_role:
                consultant_project_role.exo_role = new_role

                if old_role.code == settings.ROL_CH_PROJECT_DIRECTOR:
                    consultant_project_role.exo_role_other_name = 'Project Director'
                elif old_role.code == settings.ROL_CH_LEARNING_DESIGNER:
                    consultant_project_role.exo_role_other_name = 'Learning Designer'

                consultant_project_role.save(update_fields=['exo_role', 'exo_role_other_name'])

        self.stdout.write(self.style.SUCCESS('ConsultantProjectRole migrated'))

    def migrate_user_project_roles(self):
        self.stdout.write(self.style.WARNING('UserProjectRole migration ...'))

        for user_project_role in UserProjectRole.objects.filter(role__isnull=False):
            old_role = user_project_role.role
            new_role = self.get_exo_role(old_role.code)

            if new_role:
                user_project_role.exo_role = new_role

                if old_role.code == settings.ROL_CH_USER_MEMBER_STAFF:
                    user_project_role.exo_role_other_name = 'Staff'

                user_project_role.save(update_fields=['exo_role', 'exo_role_other_name'])

        self.stdout.write(self.style.SUCCESS('UserProjectRole migrated'))

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('MIGRATING PLATFORM ROLES, casi nah! \n'))

        self.migrate_consultant_roles()
        self.migrate_consultant_roles_trainers()
        self.migrate_consultant_project_roles()
        self.migrate_user_project_roles()

        call_command('create_user_badges')
        call_command('sync_jobs')
