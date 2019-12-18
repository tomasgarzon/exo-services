from django.core.management.base import BaseCommand

from ...models import ConsultantExOProfile


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write('\n Reset Consultant Activities: \n\n')  # noqa
        for consultant_profile in ConsultantExOProfile.objects.filter(exo_activities__isnull=False):
            self.stdout.write('  {} .... done \n'.format(
                consultant_profile.consultant.user.email))
            consultant_profile._exo_activities.clear()

        self.stdout.write('\n Finish!! \n\n')
