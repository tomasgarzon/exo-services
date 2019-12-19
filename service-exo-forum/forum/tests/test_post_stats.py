import time

from django import test
from django.test import tag

from actstream.models import followers
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from test_utils.redis_test_case_mixin import RedisTestCaseMixin
from circles.models import Circle
from utils.faker_factory import faker
from utils.dates import increase_date

from ..models import Post


class PostStatTest(RedisTestCaseMixin, test.TestCase):

    def setUp(self):
        self.circle = Circle.objects.first()
        self.user = FakeUserFactory.create(is_active=True)
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        post_id = post.pk
        self.post = Post.objects.get(pk=post_id)

    @tag('sequencial')
    def test_see_stats(self):
        # PREPARE DATA
        user = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user)

        # DO ACTION
        self.post.see(user)

        # ASSERTS
        self.assertEqual(self.post.count_views, 2)
        self.assertTrue(self.post.has_seen(user))

    def test_replies_stats(self):
        # PREPARE DATA
        user = FakeUserFactory.create(is_active=True)
        timestamp = increase_date(days=1)
        self.circle.add_user(user)

        # DO ACTION
        self.post.reply(user, faker.text(), timestamp=timestamp)

        # ASSERTS
        self.post.refresh_from_db()
        self.assertEqual(self.post.counter_replies, 1)
        self.assertEqual(
            set(followers(self.post)),
            {user, self.user},
        )
        modified = self.post.modified
        self.assertEqual(modified.date(), increase_date(days=1).date())
        answer = self.post.answers.first()
        self.assertEqual(answer.created.date(), increase_date(days=1).date())
        self.assertEqual(answer.modified.date(), increase_date(days=1).date())

    @test.override_settings(FORUM_NEW_POST_DELAY=1)
    def test_post_edited(self):
        # PRE ASSERTIONS
        self.assertIsNone(self.post.edited)

        # DO ACTION
        Post.objects.update_post(
            self.post,
            user_from=self.user,
            title=faker.sentence(),
            description=faker.text(),
            tags=self.post.tags.all(),
        )

        # ASSERTS
        time.sleep(2)
        self.assertIsNotNone(self.post.edited)

    @test.override_settings(FORUM_NEW_POST_DELAY=1)
    def test_post_edited_serveral_times(self):
        # PREPARE DATA
        Post.objects.update_post(
            self.post,
            user_from=self.user,
            title=faker.sentence(),
            description=faker.text(),
            tags=self.post.tags.all(),
        )
        time.sleep(2)
        first_edit = self.post.edited

        # DO ACTION
        Post.objects.update_post(
            self.post,
            user_from=self.user,
            title=faker.sentence(),
            description=faker.text(),
            tags=self.post.tags.all(),
        )

        # ASSERTS
        time.sleep(2)
        self.assertNotEqual(first_edit.timestamp, self.post.edited.timestamp)

    def test_post_last_answer_seen(self):
        # PREPARE DATA
        user_to_reply = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user_to_reply)
        user = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user)

        # PRE ASSERTIONS
        self.assertEqual(self.post.answers.count(), 0)
        self.assertIsNone(self.post.last_answer_seen(user))

        # DO ACTION
        self.post.reply(
            user_to_reply,
            faker.text(),
        )

        # ASSERTS
        self.assertEqual(self.post.answers.count(), 1)
        self.assertIsNone(self.post.last_answer_seen(user))

    def test_last_answer_seen_after_visit_post(self):
        # PREPARE DATA
        user_to_reply = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user_to_reply)
        user = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user)

        answer = self.post.reply(
            user_to_reply,
            faker.text(),
        )

        # DO ACTION
        answer.see(user)

        # ASSERTS
        self.assertEqual(self.post.answers.count(), 1)
        self.assertIsNotNone(self.post.last_answer_seen(user))

    def test_last_answer_seen_after_several_visit_post(self):
        # PREPARE DATA
        user_to_reply = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user_to_reply)
        user = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user)

        answer = self.post.reply(user_to_reply, faker.text())
        answer.see(user)
        first_user_action_post_visit = self.post.last_answer_seen(user)

        answer = self.post.reply(user_to_reply, faker.text())
        answer.see(user)

        # DO ACTION
        self.post.see(user)

        # ASSERTS
        last_action_answer_seen = self.post.last_answer_seen(user)
        self.assertIsNotNone(first_user_action_post_visit)
        self.assertNotEqual(first_user_action_post_visit, last_action_answer_seen)

    def test_post_new_answers(self):
        # PREPARE DATA
        user_to_reply = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user_to_reply)
        user = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user)

        self.post.reply(user_to_reply, faker.text())
        self.post.reply(user_to_reply, faker.text())

        # PRE ASSERTS
        self.assertEqual(
            list(self.post.new_answers(user)),
            list(self.post.answers.all().values_list('pk', flat=True)))

        # DO ACTION
        self.post.see(user)

        # ASSERTS
        self.assertEqual(len(self.post.new_answers(user)), 2)

    def test_post_unseen_answers(self):
        # PREPARE DATA
        user_to_reply = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user_to_reply)
        user = FakeUserFactory.create(is_active=True)
        self.circle.add_user(user)

        self.post.reply(user_to_reply, faker.text())
        self.post.reply(user_to_reply, faker.text())

        # PRE ASSERTS
        self.assertEqual(self.post.answers_unseen(user), 2)

        # DO ACTION
        for answer in self.post.answers.all():
            answer.see(user)

        # ASSERTS
        self.assertEqual(self.post.answers_unseen(user), 0)
