from celery import current_app as app

from .reminder_one_day_before import ReminderOneDayBeforeTask
from .reminder_one_hour_before import ReminderOneHourBeforeTask
from .summary_one_hour_after import SummaryOneHourAfterTask

app.tasks.register(ReminderOneDayBeforeTask())
app.tasks.register(ReminderOneHourBeforeTask())
app.tasks.register(SummaryOneHourAfterTask())
