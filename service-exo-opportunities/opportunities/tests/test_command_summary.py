import requests_mock

from django.test import TestCase
from django.utils.six import StringIO
from django.conf import settings

from exo_role.models import ExORole
from utils.test_mixin import UserTestMixin

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..management.commands.opportunity_send_summary import Command


class OpportunityCommandSummaryTest(
        UserTestMixin,
        OpportunityTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_send_summary(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        roles = [
            [settings.EXO_ROLE_CODE_ADVISOR, 2],
            [settings.EXO_ROLE_CODE_SPRINT_COACH, 1],
            [settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH, 1],
            [settings.EXO_ROLE_CODE_SPRINT_COACH, 3],
            [settings.EXO_ROLE_CODE_ADVISOR, 2]
        ]
        total_expected = 9
        roles_expected = [{
            'name': ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH).name,
            'total': 4
        }, {
            'name': ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH).name,
            'total': 1
        }, {
            'name': ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR).name,
            'total': 4
        }]

        # Opp requested with deadline for today
        for role, num_positions in roles:
            exo_role = ExORole.objects.get(code=role)
            self.create_opportunity(role=exo_role, num_positions=num_positions)

        out = StringIO()
        err = StringIO()

        # ACTION
        command = Command(stdout=out, stderr=err)

        # ASSERTS
        total, roles_received, opportunities = command.get_opportunities_open_and_not_sent()

        self.assertEqual(total, total_expected)
        self.assertEqual(opportunities.count(), len(roles))
        self.assertEqual(
            len(roles_expected),
            len(roles_received))

        for rol_expected in roles_expected:
            exists = False
            for rol_received in roles_received:
                if rol_received['name'] == rol_expected['name']:
                    exists = True
                    break

            # ASSERTS
            self.assertTrue(exists)
            self.assertEqual(rol_received['total'], rol_expected['total'])

        data_signed = command.get_data_signed(total, roles_received, opportunities)

        # ASSERTS
        self.assertEqual(data_signed['total'], total)
        self.assertEqual(data_signed['other_total'], 1)

        roles = data_signed.get('roles')
        first_role = roles[0]

        # ASSERTS
        self.assertEqual(
            first_role['total'], 4)
        self.assertTrue(
            first_role['name'] in [
                ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH).name,
                ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR).name
            ]
        )
        self.assertEqual(len(first_role['opportunities']), 2)

        # ASSERTS
        second_role = roles[1]
        self.assertEqual(
            second_role['total'], 4)
        self.assertTrue(
            second_role['name'] in [
                ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH).name,
                ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR).name
            ])
        self.assertEqual(
            len(second_role['opportunities']), 2)
