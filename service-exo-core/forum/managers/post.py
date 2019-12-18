from django.db import models
from django.contrib.contenttypes.models import ContentType

from utils.descriptors import CustomFilterDescriptorMixin
from project.models import Project

from ..queryset.post import PostQuerySet
from ..conf import settings


class PostManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    queryset_class = PostQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': '_type',
            'options': settings.FORUM_POST_CH_TYPE,
        },
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        ).filter_by_status_published()

    def create_circle_post(self, user_from, circle, *args, **kwargs):
        circle.check_user_can_post(user_from)
        kwargs['_type'] = settings.FORUM_CH_CIRCLE
        kwargs['created_by'] = user_from
        return self._create_post(user_from, circle, *args, **kwargs)

    def create_announcement_post(self, user_from, *args, **kwargs):
        if not user_from.is_staff:
            raise Exception('Operation Not allowed')
        kwargs['_type'] = settings.FORUM_CH_ANNOUNCEMENT
        kwargs['created_by'] = user_from
        return self._create_post(user_from, *args, **kwargs)

    def create_project_team_post(self, user_from, team, *args, **kwargs):
        kwargs['_type'] = settings.FORUM_CH_PROJECT
        kwargs['created_by'] = user_from
        project_perms = team.project.check_user_can_post(user_from)
        team_perms = team.check_user_can_post(user_from)
        if not project_perms or not team_perms:
            raise Exception("User can't do this operation")
        return self._create_post(user_from, team, *args, **kwargs)

    def create_project_qa_session_post(
            self, user_from, qa_session_team, *args, **kwargs):
        kwargs['_type'] = settings.FORUM_CH_QA_SESSION
        kwargs['created_by'] = user_from
        team = qa_session_team.team
        project_perms = team.project.check_user_can_post(user_from)
        team_perms = team.check_user_can_post(user_from)
        if not project_perms or not team_perms:
            raise Exception("User can't do this operation")
        return self._create_post(user_from, qa_session_team, *args, **kwargs)

    def _create_post(self, user_from, related_object=None, *args, **kwargs):
        tags = kwargs.pop('tags', [])
        email_notification = kwargs.pop('email_notification', True)
        is_draft = kwargs.pop('is_draft', False)
        if is_draft:
            kwargs['status'] = settings.FORUM_CH_DRAFT

        if related_object:
            ct = ContentType.objects.get_for_model(related_object)
            kwargs['content_type'] = ct
            kwargs['object_id'] = related_object.pk

        post = super().create(*args, **kwargs)
        post.tags.add(*tags)
        post.see(user_from, notify=False)
        post.action_create(user_from)

        if email_notification:
            post.send_email_created()
        return post

    def update_post(self, post, *args, **kwargs):
        user_from = kwargs.get('user_from')
        post.can_update_or_remove(user_from)
        post.title = kwargs.get('title')
        post.description = kwargs.get('description')
        post.save()
        post.tags.clear()
        tags = kwargs.get('tags')
        post.tags.add(*tags)
        post.action_update(user_from)
        return post

    def filter_by_circle(self, circle):
        return self.get_queryset().filter_by_circle(circle)

    def filter_by_circles(self, circles):
        return self.get_queryset().filter_by_circles(circles)

    def filter_by__type(self, post_type):
        return self.get_queryset().filter_by__type(post_type)

    def filter_questions_by_user(self, user):
        consultant_with_consulting_activity = user.has_perm(
            settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_CONSULTING)
        if not consultant_with_consulting_activity and not user.is_superuser:
            return []
        projects = Project.objects.filter_by_user(user)
        return self.get_queryset().filter_by_projects(projects)

    def filter_by_related_question(self, post, size=5):
        # this method is horribly inefficient
        tags = set(post.tags.all().values_list('id', flat=True))
        if post.is_project:
            queryset = self.filter_by__type_project().exclude(
                pk=post.pk
            ).prefetch_related('tags')
        elif post.is_circle:
            queryset = self.filter_by_circle(
                post.content_object
            ).exclude(pk=post.pk).prefetch_related('tags')
        else:
            queryset = []
        posts = {
            p.pk: p.tags.all().values_list('id', flat=True)
            for p in queryset
        }
        matches = {}
        for post_pk, tags_ids in posts.items():
            common_tags = list(set(tags_ids).intersection(tags))
            if len(common_tags) > 0:
                matches[post_pk] = len(common_tags)
        sorted_post = [
            k for k in sorted(matches, key=matches.get, reverse=True)]
        results = []
        for post_id in sorted_post:
            new_post = self.get(pk=post_id)
            results.append(new_post)
            if len(results) == size:
                break
        return results

    def filter_by_user_subscribed(self, user):
        return self.get_queryset().filter_by_user_subscribed(user)

    def filter_by_qa_session_team(self, qa_session, team):
        return self.get_queryset().filter_by_qa_session_team(qa_session, team)

    def filter_by_qa_session(self, qa_session):
        return self.get_queryset().filter_by_qa_session(qa_session)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_search(self, search):
        return self.get_queryset().filter_by_search(search)


class AllPostManager(PostManager):
    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
