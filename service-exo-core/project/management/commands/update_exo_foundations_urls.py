from django.core.management.base import BaseCommand

from project.models import Project


class Command(BaseCommand):

    help = 'Update links related to Typeform for ExOFoundation project (id#145) to manage \
            the url from our backend instead of use the Typeform url directly.'

    def handle(self, *args, **options):
        project = Project.objects.get(pk=145)
        project_step_certify = project.steps.last()
        certify_assignment = project_step_certify.assignments_step.first()
        block = certify_assignment.blocks.get(order=2)
        block_data = block.assignments_text
        block_data.text = block_data.text.replace(
            '<a href="https://openexo.typeform.com/to/m23mE5" target="_blank">here</a>',
            '<a data-popup="typeform" href="api/typeform/get/exo_certification_certification_quiz_en/" target="_blank">here</a>'    # noqa
        )
        block_data.text = block_data.text.replace(
            '<a href="https://openexo.typeform.com/to/H0mEnJ" target="_blank">here</a>',
            '<a data-popup="typeform" href="api/typeform/get/exo_certification_certification_assessment_en/" target="_blank">here</a>'    # noqa
        )
        block_data.text = block_data.text.replace(
            '<a href="https://learn.openexo.com/teach/" target="_blank">here</a>',
            '<a href="api/typeform/get/exo_certification_teaching_assignment_en/" target="_blank">here</a>'    # noqa
        )
        block_data.text = block_data.text.replace(
            '<a href="https://openexo.typeform.com/to/MIp7eA" target="_blank">here</a>',
            '<a data-popup="typeform" href="api/typeform/get/exo_certification_feedback_en/" target="_blank">here</a>'    # noqa
        )

        block_data.save(update_fields=['text'])
        self.stdout.write(self.style.SUCCESS('Done!!\n\n'))
