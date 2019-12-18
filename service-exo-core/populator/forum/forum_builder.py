from datetime import datetime

from forum.models import Post
from keywords.models import Keyword
from consultant.models import Consultant
from files.models import UploadedFile
from populate.populator.builder import Builder


class PostBuilder(Builder):

    def create_object(self):
        user = self._get_user(self.data.get('user'))
        circle = self.data.get('circle')
        team = self.data.get('team')
        qa_session = self.data.get('qa_session')
        date = self.data.get('date', datetime.now())

        if circle:
            post = self.create_circle_post(
                user=user,
                circle=circle,
                title=self.data.get('title'),
                description=self.data.get('description'),
                created=date,
                tags=self.data.get('tags', []))
        elif qa_session and team:

            post = self.create_qa_session_post(
                user=user,
                qa_session_team=qa_session.teams.get(team=team),
                created=date,
                title=self.data.get('title'),
                desc=self.data.get('description'),
                tags=self.data.get('tags', []),
            )
        elif team:
            # Ecosystem question (open)
            post = self.create_project_team_post(
                user=user,
                team=team,
                created=date,
                title=self.data.get('title'),
                description=self.data.get('description'),
                tags=self.data.get('tags', []))
        else:
            post = self.create_announcement_post(
                user=user,
                created=date,
                title=self.data.get('title'),
                description=self.data.get('description'),
                tags=self.data.get('tags', []))

        self.update_files(
            post=post,
            files=self.data.get('files', []))
        return self.update_post_activities(
            post=post,
            activities=self.data.get('activities', []))

    def create_qa_session_post(self, user, qa_session_team, title, desc, created, tags):
        post = Post.objects.create_project_qa_session_post(
            user_from=user,
            qa_session_team=qa_session_team,
            title=title,
            created=created,
            description=desc,
            tags=self._get_keywords(tags),
        )
        return self._update_modified_date(post, created)

    def create_circle_post(self, user, circle, title, description, created, tags):
        post = Post.objects.create_circle_post(
            user_from=user,
            circle=circle,
            title=title,
            created=created,
            description=description,
            tags=self._get_keywords(tags))
        return self._update_modified_date(post, created)

    def create_announcement_post(self, user, title, description, created, tags):
        post = Post.objects.create_announcement_post(
            user_from=user,
            title=title,
            created=created,
            description=description,
            tags=self._get_keywords(tags))
        return self._update_modified_date(post, created)

    def create_project_team_post(self, user, team, title, description, created, tags):
        post = Post.objects.create_project_team_post(
            user_from=user,
            team=team,
            title=title,
            created=created,
            description=description,
            tags=self._get_keywords(tags))
        return self._update_modified_date(post, created)

    def _update_modified_date(self, post, created):
        Post.objects.filter(pk=post.id).update(modified=created)
        post = Post.objects.get(pk=post.id)
        return post

    def _get_keywords(self, tags):
        return [Keyword.objects.get(name=tag) for tag in tags]

    def _get_user(self, user):
        return user.user if isinstance(user, Consultant) else user

    def update_post_activities(self, post, activities):
        for activity in activities:
            reply = activity.get('reply')
            user = self._get_user(activity.get('user'))
            timestamp = activity.get('date', None)
            if reply:
                post.reply(user_from=user, comment=reply, timestamp=timestamp)
            else:
                post.see(user_from=user, timestamp=timestamp)
            if timestamp:
                Post.objects.filter(pk=post.id).update(modified=timestamp)
                post = Post.objects.get(pk=post.id)

        return post

    def update_files(self, post, files):
        for file_data in files:
            UploadedFile.create(
                created_by=post.created_by,
                filename=file_data.get('filename'),
                mimetype=file_data.get('mimetype'),
                filestack_url=file_data.get('filestack_url'),
                filestack_status='Stored',
                related_to=post)
