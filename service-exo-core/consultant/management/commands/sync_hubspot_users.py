from datetime import datetime

from django.core.management.base import BaseCommand

from certification.models import CertificationCredential
from consultant.hubspot.contact import (
    Contact,
    HubSpotException,
    HubSpotUserDoesNotExistException,
    COMMUNITY_LIFE_CYCLE_MEMBER,
    COMMUNITY_LIFE_CYCLE_LEAD,
    ON_BOARDING_ENTRY_POINT_CERTIFIED,
    ON_BOARDING_ENTRY_POINT_ALREADY_MEMBER,
    CERTIFICATION_LEAD_EXO_FOUNDATIONS,
    CERTIFIED_IN_EXO_FOUNDATIONS,
    CERTIFIED_IN_EXO_COACH,
)
from consultant.models import Consultant
from core.management.commands.progress_bar import ProgressBar


class Command(BaseCommand):

    def handle(self, *args, **options):
        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        log.write('\nExecution date {}\n\n'.format(datetime.now().date()))

        self.stdout.write(self.style.WARNING(
            'This script will sync all Platform Consultants at HubSpot \n',
        ))
        self.stdout.write(self.style.NOTICE('Attention!!'))
        self.stdout.write(self.style.NOTICE(
            'You are going to generate PUBLIC changes',
        ))

        proceed = input('Do you want to proceed? (Y/[N]): ')
        if proceed.lower() == 'y':
            queryset = Consultant.all_objects.all()
            bar = ProgressBar(title='Updating users to HubSpot', total=queryset.count())

            for consultant in queryset:
                bar.step(message=consultant.user.email)
                log.write('Sync {} \n'.format(consultant.user.email))
                try:
                    hubspot_user = Contact.get_contact(consultant.user.email)
                    log.write('    Contact EXIST at hubspot \n')
                except HubSpotUserDoesNotExistException:
                    hubspot_user = Contact(
                        email=consultant.user.email,
                        full_name=consultant.user.full_name,
                    )
                    hubspot_user.create_contact()
                    log.write('    Contact CREATED at hubspot \n')

                try:
                    community_life_cycle = COMMUNITY_LIFE_CYCLE_MEMBER if consultant.is_active else COMMUNITY_LIFE_CYCLE_LEAD  # noqa
                    hubspot_user.update_property('community_life_cycle', community_life_cycle)
                    log.write('    Property {} setted with value {} \n'.format(
                        'community_life_cycle',
                        community_life_cycle
                    ))
                except HubSpotException:
                    log.write('    ERROR: Cannot set Property {} with value {} \n'.format(
                        'community_life_cycle', community_life_cycle
                    ))

                if hasattr(consultant.user, 'registration_process'):
                    self.sync_user_with_registration_process(consultant, hubspot_user, log)
                else:
                    self.sync_user_without_registration_process(consultant, hubspot_user, log)

                try:
                    certified_in = self.set_certified_in_property(consultant, hubspot_user)
                    log.write('    Property {} setted with value {} \n'.format('certified_in', certified_in))
                except HubSpotException:
                    log.write('    ERROR: Cannot set Property {} with value {} \n'.format(
                        'certified_in', certified_in
                    ))

            log.write('\nDone!!\n\n')

        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n')

        log.close()

    def sync_user_without_registration_process(self, consultant, hubspot_user, log):
        # This is an OLD Consultant
        try:
            hubspot_user.update_property('onboarding_entry_point', ON_BOARDING_ENTRY_POINT_ALREADY_MEMBER)
            log.write('    Property {} setted with value {} \n'.format(
                'onboarding_entry_point',
                ON_BOARDING_ENTRY_POINT_ALREADY_MEMBER,
            ))
        except HubSpotException:
            log.write('    ERROR: Cannot set Property {} with value {} \n'.format(
                'onboarding_entry_point', ON_BOARDING_ENTRY_POINT_ALREADY_MEMBER
            ))

    def sync_user_with_registration_process(self, consultant, hubspot_user, log):
        onboarding_entry_point = consultant.user.registration_process.real_entry_point
        try:
            hubspot_user.update_property('onboarding_entry_point', onboarding_entry_point)
            log.write('    Property {} setted with value {} \n'.format(
                'onboarding_entry_point',
                onboarding_entry_point
            ))
        except HubSpotException:
            log.write('    ERROR: Cannot set Property {} with value {} \n'.format(
                'onboarding_entry_point', onboarding_entry_point
            ))

        if onboarding_entry_point == ON_BOARDING_ENTRY_POINT_CERTIFIED:
            try:
                hubspot_user.update_property(
                    'certification_leads',
                    CERTIFICATION_LEAD_EXO_FOUNDATIONS,
                )
                log.write('    Property {} setted with value {} \n'.format(
                    'certification_leads',
                    CERTIFICATION_LEAD_EXO_FOUNDATIONS,
                ))
            except HubSpotException:
                log.write('    ERROR: Cannot set Property {} with value {} \n'.format(
                    'certification_leads', CERTIFICATION_LEAD_EXO_FOUNDATIONS
                ))

    def set_certified_in_property(self, consultant, hubspot_user):
        certified_in = None
        hubspot_user.update_property('certified_in', '')

        try:
            CertificationCredential.objects.get(
                user=consultant.user,
                group___type='consultantrole-advisor',
            )
            certified_in = CERTIFIED_IN_EXO_FOUNDATIONS
        except CertificationCredential.DoesNotExist:
            pass

        try:
            assert CertificationCredential.objects.filter(
                user=consultant.user,
                group___type__in=[
                    'consultantrole-sprint-coach',
                    'consultantrole-trainer'
                ]
            ).exists()
            certified_in = CERTIFIED_IN_EXO_COACH
        except AssertionError:
            pass

        hubspot_user.update_property('certified_in', certified_in)
        return certified_in
