from django.conf import settings

import requests_mock
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityUserActionsAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_opportunities_requested(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(opp.created_by)
        self.assertEqual(
            set(actions),
            {
                settings.OPPORTUNITIES_ACTION_CH_EDIT,
                settings.OPPORTUNITIES_ACTION_CH_REMOVE,
                settings.OPPORTUNITIES_ACTION_CH_CLOSE,
            })

        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(opp.created_by, True)
        self.assertEqual(
            actions,
            [])

        # CONSULTANT
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(user, True)
        self.assertEqual(
            actions,
            [settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN])

    def assertNoActions(self, actions):
        self.assertEqual(
            actions,
            [])

    def assertActionsAdmin(self, opp, actions):
        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(opp.created_by)
        self.assertEqual(
            set(actions),
            {
                settings.OPPORTUNITIES_ACTION_CH_EDIT,
                settings.OPPORTUNITIES_ACTION_CH_REMOVE,
                settings.OPPORTUNITIES_ACTION_CH_CLOSE,
            })
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(opp.created_by, True)
        self.assertNoActions(actions)

    @requests_mock.Mocker()
    def test_opportunities_requested_with_applicant_assigned(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)

        self.assertActionsAdmin(opp, opp.created_by)

        with self.settings(POPULATOR_MODE=False):
            actions = app.user_actions(opp.created_by)
        self.assertEqual(len(actions), 2)
        self.assertEqual(
            actions,
            [settings.OPPORTUNITIES_ACTION_CH_REJECT,
             settings.OPPORTUNITIES_ACTION_CH_SOW_EDIT])

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            actions = app.user_actions(user)
        self.assertEqual(actions, [])

        # CONSULTANT
        new_user = self.get_user()
        request_mock_account.add_mock(
            new_user, is_consultant=True, is_superuser=False)
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(new_user, True)
        self.assertEqual(
            actions,
            [settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN])

    @requests_mock.Mocker()
    def test_opportunities_requested_with_applicant_rejected(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.reject(self.super_user, app)

        self.assertActionsAdmin(opp, opp.created_by)
        with self.settings(POPULATOR_MODE=False):
            actions = app.user_actions(opp.created_by)
        self.assertEqual(
            actions,
            [settings.OPPORTUNITIES_ACTION_CH_ASSIGN])

        # REJECTED
        with self.settings(POPULATOR_MODE=False):
            self.assertNoActions(opp.user_actions(user, True))
            self.assertNoActions(app.user_actions(user))

        # CONSULTANT
        new_user = self.get_user()
        request_mock_account.add_mock(
            new_user, is_consultant=True, is_superuser=False)
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(new_user, True)
        self.assertEqual(
            actions,
            [settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN])

    @requests_mock.Mocker()
    def test_opportunities_close_with_applicant_assigned(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        opp.close(self.super_user)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(opp.created_by)
        self.assertEqual(
            len(actions),
            1)
        with self.settings(POPULATOR_MODE=False):
            actions = opp.user_actions(opp.created_by, True)
            self.assertEqual(
                actions,
                [settings.OPPORTUNITIES_ACTION_CH_RE_OPEN])
            actions = app.user_actions(opp.created_by)
            self.assertEqual(
                set(actions),
                {
                    settings.OPPORTUNITIES_ACTION_CH_REJECT,
                    settings.OPPORTUNITIES_ACTION_CH_SOW_EDIT,
                })

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertNoActions(opp.user_actions(user, True))
            self.assertNoActions(app.user_actions(user))

        # CONSULTANT
        new_user = self.get_user()
        request_mock_account.add_mock(
            new_user, is_consultant=True, is_superuser=False)
        with self.settings(POPULATOR_MODE=False):
            self.assertNoActions(opp.user_actions(new_user, True))

    @requests_mock.Mocker()
    def test_opportunities_remove_with_applicant_assigned(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        opp.remove(self.super_user)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            self.assertNoActions(opp.user_actions(opp.created_by, True))
            self.assertNoActions(opp.user_actions(opp.created_by))
            self.assertNoActions(app.user_actions(opp.created_by))

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertNoActions(opp.user_actions(user, True))
            self.assertNoActions(app.user_actions(user))

        # CONSULTANT
        new_user = self.get_user()
        request_mock_account.add_mock(
            new_user, is_consultant=True, is_superuser=False)
        with self.settings(POPULATOR_MODE=False):
            self.assertNoActions(opp.user_actions(new_user, True))

    @requests_mock.Mocker()
    def test_completed_not_feedback_yet(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        app.set_completed(self.super_user)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(opp.created_by),
                [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            )

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(user),
                [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            )

    @requests_mock.Mocker()
    def test_closed_completed_not_feedback_yet(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(num_positions=1)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        app.set_completed(self.super_user)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(opp.created_by),
                [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            )

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(user),
                [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            )

    @requests_mock.Mocker()
    def test_completed_applicant_given_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        app.set_completed(self.super_user)
        app.set_status(
            user, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_APP)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(opp.created_by),
                [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            )

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(user),
                []
            )

    @requests_mock.Mocker()
    def test_completed_requester_given_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        app.set_completed(self.super_user)
        app.set_status(
            opp.created_by, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_REQUESTER)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(opp.created_by),
                []
            )

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(user),
                [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            )

    @requests_mock.Mocker()
    def test_completed_both_given_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)
        app.set_completed(self.super_user)
        app.set_status(
            opp.created_by, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY)
        app.refresh_from_db()

        # ADMIN/CREATED BY
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(opp.created_by),
                []
            )

        # ASSIGNED
        with self.settings(POPULATOR_MODE=False):
            self.assertEqual(
                app.user_actions(user),
                []
            )
