from django import test
from django.utils import timezone
from dateutil import parser

from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin

from ..conf import settings


class StepCreationTest(SuperUserTestMixin, test.TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_sprint_automated_steps(self):
        # PREPARE DATA
        sprint = FakeSprintAutomatedFactory.create(start=None)
        project = sprint.project_ptr
        project.update_assignments_template(
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)
        start = timezone.now()
        project.set_started(
            user=self.super_user,
            start_date=start,
        )
        dates = [
            ('2018-11-07 07:00:17+00:00', '2018-11-05 09:00:04+00:00', 1),
            ('2018-11-05 09:00:04+00:00', '2018-11-05 11:00:04+00:00', 2),
            ('2018-11-05 11:00:34+00:00', '2018-11-06 18:00:34+00:00', 3),
            ('2018-11-07 09:00:39+00:00', '2018-11-16 18:00:39+00:00', 4),
            ('2018-11-18 09:00:27+00:00', None, 5),
            ('2018-12-03 09:00:57+00:00', None, 6),
            ('2018-11-26 09:00:10+00:00', None, 7),
            ('2018-12-03 09:00:43+00:00', None, 8),
            ('2018-12-10 09:00:35+00:00', None, 9),
            ('2018-12-17 09:00:22+00:00', None, 10),
            ('2018-12-24 09:00:46+00:00', None, 11),
            ('2018-12-31 09:00:00+00:00', None, 12),
            ('2019-01-07 09:00:12+00:00', None, 13),
        ]
        for index, k in enumerate(project.steps.all().order_by('index')):
            k.start = parser.parse(dates[index][0])
            end = dates[index][1]
            if end is not None:
                k.end = parser.parse(end)
            k.save()

        inputs = [
            '2018-11-06 09:00:10+00:00',
            '2018-11-25 09:00:10+00:00',
            '2018-12-16 09:00:10+00:00',
        ]

        output_excepted = [3, 5, 9]

        # ASSERTS
        for index, date in enumerate(inputs):
            project_step = project.current_step(parser.parse(date))
            self.assertEqual(project_step.index, output_excepted[index])
