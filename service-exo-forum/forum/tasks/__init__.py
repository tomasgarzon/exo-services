from celery import current_app as app

from .ecosystem_weekly_summary import EcosystemWeeklySummaryTask
from .post_tasks import (
    PostSendEmailCreatedTask,
    PostSendEmailReplyTask,
    PostMentionSendEmailTask,
    AnswerMentionSendEmailTask,
    NotifyPostChangeTask
)
from .answer_tasks import (
    PostAnswerRatingTask,
    NotifyAnswerChangeTask,
    MarkAnswerAsReadTask)


app.tasks.register(EcosystemWeeklySummaryTask())
app.tasks.register(PostSendEmailCreatedTask())
app.tasks.register(PostSendEmailReplyTask())
app.tasks.register(PostMentionSendEmailTask())
app.tasks.register(AnswerMentionSendEmailTask())
app.tasks.register(PostAnswerRatingTask())
app.tasks.register(NotifyPostChangeTask())
app.tasks.register(NotifyAnswerChangeTask())
app.tasks.register(MarkAnswerAsReadTask())
