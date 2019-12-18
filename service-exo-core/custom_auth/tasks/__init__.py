from celery import current_app as app

from .matching_linkedin import MatchingLinkedinTask  # noqa
from .migrate_users import MigrateUserTask  # noqa
from .user_location import UserLocationTask  # noqa


app.tasks.register(MatchingLinkedinTask())
app.tasks.register(MigrateUserTask())
app.tasks.register(UserLocationTask())
