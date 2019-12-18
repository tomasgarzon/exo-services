from celery.schedules import crontab

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

CELERYBEAT_SCHEDULE = {
    'ecosystem-weekly-update-morning': {
        'task': 'forum.tasks.ecosystem_weekly_summary.EcosystemWeeklySummaryTask',
        'schedule': crontab(minute='25', hour='23', day_of_week='sunday'),
    },
    'auth-syncronize-users': {
        'task': 'custom_auth.tasks.migrate_users.MigrateUserTask',
        'schedule': crontab(minute='15', hour='23', day_of_week='*'),
    },
    'instrumentation-data': {
        'task': 'core.tasks.instrumentation.InstrumentationTask',
        'schedule': crontab(minute='0', hour='0', day_of_week='mon'),
    }
}
