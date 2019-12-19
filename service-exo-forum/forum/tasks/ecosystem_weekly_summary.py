from django.utils import timezone
from django.db.models import Avg
from django.conf import settings

from celery import Task
from actstream.models import following

from circles.models import Circle
from utils.mail import handlers
from utils.dates import decrease_date
from consultant.models import Consultant

from ..models import Post, Answer


class EcosystemWeeklySummaryTask(Task):
    name = 'EcosystemWeeklySummaryTask'
    ignore_result = True

    def send_weekly(self, user):
        results = {
            'circles': [],
            'short_name': user.short_name,
            'disable_notification_url': '',
            'public_url': settings.FRONTEND_CIRCLES_PAGE,
        }
        circles = following(user, Circle)
        start_at = decrease_date(days=7)
        end_at = timezone.now()
        has_data_to_send = False
        for circle in circles:
            posts = Post.objects.filter_by_circle(circle).filter(
                created__gte=start_at, created__lte=end_at).count()
            replies = Answer.objects.filter_by_circle(circle).filter(
                created__gte=start_at, created__lte=end_at).count()
            if posts or replies:
                has_data_to_send = True
                circle_data = {
                    'name': circle.name,
                    'image': circle.image,
                    'new_topics': posts,
                    'new_replies': replies
                }
                results['circles'].append(circle_data)
        results['new_announcements'] = Post.objects.filter_by__type_announcement().filter(
            created__gte=start_at, created__lte=end_at).count()
        if results['new_announcements']:
            has_data_to_send = True
        results['new_questions'] = Post.objects.filter_by__type_project().filter(
            created__gte=start_at, created__lte=end_at).count()
        user_answers = Answer.objects.filter(
            created_by=user,
            post___type=settings.FORUM_CH_PROJECT).filter(
                created__gte=start_at, created__lte=end_at)
        results['your_answers'] = user_answers.count()
        results['your_rating'] = user_answers.aggregate(avg=Avg('ratings__rating'))['avg']
        if results['new_questions']:
            has_data_to_send = True
        if has_data_to_send:
            handlers.mail_handler.send_mail(
                'ecosystem_weekly_summary',
                recipients=[user.email],
                **results)

    def run(self, *args, **kwargs):
        for consultant in Consultant.objects.all():
            user = consultant.user
            self.send_weekly(user)
