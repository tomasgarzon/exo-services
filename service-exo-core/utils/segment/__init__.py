from celery import current_app as app

from .adapter import SegmentAnalytics
from .tasks import SegmentIdentifyTask, SegmentEventTask


app.tasks.register(SegmentEventTask)
app.tasks.register(SegmentIdentifyTask)
