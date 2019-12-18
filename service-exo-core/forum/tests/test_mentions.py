from django.test import TestCase
from django.core import mail
from django.conf import settings

from unittest.mock import patch

from account_config.models import ConfigParam
from circles.models import Circle
from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from exo_mentions.mixins.mentions_test_mixins import (
    DEFAULT_TYPE_PATTERN,
    DEFAULT_UUID_PATTERN,
)
from forum.models import Post
from test_utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker
from test_utils.mock_mixins import MagicMockMixin


class MentionsPostTest(UserTestMixin, MagicMockMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    def test_create_post_with_one_mention(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        user_mentioned = FakeUserFactory.create(is_active=True)
        description = '<a {}="{}" {}="{}">{}</a>'.format(
            DEFAULT_TYPE_PATTERN, user_mentioned.__class__.__name__,
            DEFAULT_UUID_PATTERN, user_mentioned.pk,
            user_mentioned.short_name,
        )

        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=description)
        post_id = post.pk

        # DO ACTIONS
        self.post = Post.objects.get(pk=post_id)

        # ASSERTS
        self.assertTrue(self.user.actor_actions.all().filter(verb=settings.MENTION_VERB).exists())
        self.assertEqual(self.user.actor_actions.all().filter(verb=settings.MENTION_VERB).count(), 1)

    def test_create_post_with_multiple_mentions(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        user_mentioned_1 = FakeUserFactory.create(is_active=True)
        user_mentioned_2 = FakeUserFactory.create(is_active=True)
        output_num_mentions = 2
        description = 'Hi \
        <a {}="{}" {}="{}">{}</a> \
        <a {}="{}" {}="{}">{}</a> \
        '.format(
            DEFAULT_TYPE_PATTERN, user_mentioned_1.__class__.__name__,
            DEFAULT_UUID_PATTERN, user_mentioned_1.pk,
            user_mentioned_1.short_name,
            DEFAULT_TYPE_PATTERN, user_mentioned_2.__class__.__name__,
            DEFAULT_UUID_PATTERN, user_mentioned_2.pk,
            user_mentioned_2.short_name,
        )

        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=description)
        post_id = post.pk

        # DO ACTIONS
        self.post = Post.objects.get(pk=post_id)

        # ASSERTS
        self.assertTrue(self.user.actor_actions.all().filter(verb=settings.MENTION_VERB).exists())
        self.assertEqual(self.user.actor_actions.all().filter(
            verb=settings.MENTION_VERB).count(), output_num_mentions)

    def test_create_post_without_mentions(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        user_mentioned = FakeUserFactory.create(is_active=True)

        description = 'hi team'.format(
            user_mentioned.pk, user_mentioned.pk, user_mentioned.short_name)

        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=description)
        post_id = post.pk

        # DO ACTIONS
        self.post = Post.objects.get(pk=post_id)

        # ASSERTS
        self.assertFalse(self.user.actor_actions.all().filter(verb=settings.MENTION_VERB).exists())

    def test_create_answer_with_mentions(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        post_id = post.pk
        self.post = Post.objects.get(pk=post_id)

        user = FakeUserFactory.create(is_active=True, password='123456')
        self.circle.add_user(user)
        user_mentioned = FakeUserFactory.create(is_active=True)

        reply_comment = 'Hi \
        <a {}="{}" {}="{}">{}</a> \
        '.format(
            DEFAULT_TYPE_PATTERN, user_mentioned.__class__.__name__,
            DEFAULT_UUID_PATTERN, user_mentioned.pk,
            user_mentioned.short_name,
        )

        # DO ACTIONS
        self.answer = self.post.reply(user, reply_comment)

        # ASSERTS
        self.assertTrue(
            user.actor_actions.all().filter(
                verb=settings.MENTION_VERB
            ).exists()
        )

    def test_create_answer_without_mentions(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        post_id = post.pk
        self.post = Post.objects.get(pk=post_id)
        user = FakeUserFactory.create(is_active=True, password='123456')
        self.circle.add_user(user)

        # DO ACTIONS
        reply_comment = 'Hi comment'
        self.answer = self.post.reply(user, reply_comment)

        # ASSERTS
        self.assertFalse(user.actor_actions.all().filter(verb=settings.MENTION_VERB).exists())

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_email_sent_for_post_new_mention(self, mock_send_mail):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        config_param = ConfigParam.objects.get(name='mention_notification')

        author = FakeConsultantFactory.create(user__is_active=True)
        config_param.set_value_for_agent(author, True)
        self.circle.add_user(author.user)

        user_mentioned_1 = FakeConsultantFactory.create(user__is_active=True)
        self.circle.add_user(user_mentioned_1.user)
        config_param.set_value_for_agent(user_mentioned_1, True)

        description = 'Hi \
        <a {}="{}" {}="{}">{}</a> \
        & <a {}="{}" {}="{}">{}</a> \
        '.format(
            DEFAULT_TYPE_PATTERN, user_mentioned_1.user.__class__.__name__,
            DEFAULT_UUID_PATTERN, user_mentioned_1.user.pk,
            user_mentioned_1.user.short_name,
            DEFAULT_TYPE_PATTERN, author.user.__class__.__name__,
            DEFAULT_UUID_PATTERN, author.user.pk,
            self.user.short_name)

        mail.outbox = []

        # DO ACTIONS
        post = Post.objects.create_circle_post(
            user_from=author.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=description)

        # ASSERTS
        self.assertEqual(mock_send_mail.called, 1)
        self.assertEqual(
            self.get_mock_kwarg(mock_send_mail, 'created_by_role'),
            post.created_by.user_title)

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_email_sent_for_new_answer_with_mentions(self, mock_send_mail):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        post_id = post.pk
        self.post = Post.objects.get(pk=post_id)

        config_param = ConfigParam.objects.get(name='mention_notification')

        author = FakeConsultantFactory.create(user__is_active=True)
        config_param.set_value_for_agent(author, True)
        self.circle.add_user(author.user)

        user_mentioned = FakeConsultantFactory.create(user__is_active=True)
        config_param.set_value_for_agent(user_mentioned, True)
        self.circle.add_user(user_mentioned.user)

        reply_comment = 'Hi \
        <a {}="{}" {}="{}">{}</a> \
        & <a {}="{}" {}="{}">{}</a> \
        '.format(
            DEFAULT_TYPE_PATTERN, user_mentioned.user.__class__.__name__,
            DEFAULT_UUID_PATTERN, user_mentioned.user.pk,
            user_mentioned.user.short_name,
            DEFAULT_TYPE_PATTERN, author.user.__class__.__name__,
            DEFAULT_UUID_PATTERN, author.user.pk,
            self.user.short_name)

        # DO ACTIONS
        self.answer = self.post.reply(author.user, reply_comment)

        # ASSERTS
        self.assertEqual(mock_send_mail.called, 1)
        self.assertEqual(
            self.get_mock_kwarg(mock_send_mail, 'created_by_role'),
            self.answer.created_by.user_title
        )
