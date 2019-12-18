import os

from .local import DEBUG

if DEBUG:
    LOG_DIR = './logs/'
else:
    LOG_DIR = '/var/log/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(name)s-%(levelname)s [%(filename)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
        },
        'service': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'service.log'),
            'formatter': 'verbose'
        },
        'registration_process': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'registration.log'),
            'formatter': 'verbose',
        },
        'network': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'network.log'),
            'formatter': 'verbose',
        },
        'users': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'users.log'),
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'files': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'files.log'),
            'formatter': 'verbose',
        },
        'typeform_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'typeform.log'),
            'formatter': 'verbose',
        },
        'validator': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'validation.log'),
            'formatter': 'verbose',
        },
        'social': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'social.log'),
            'formatter': 'verbose',
        },
        'library': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'library.log'),
            'formatter': 'verbose',
        },
        'mail': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'mail.log'),
            'formatter': 'verbose',
        },
        'zoom': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'zoom.log'),
            'formatter': 'verbose',
        },
        'countries': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'countries.log'),
            'formatter': 'verbose',
        },
        'accredible': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'accredible.log'),
            'formatter': 'verbose',
        },
        'queries': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'queries.log'),
            'formatter': 'verbose',
        },
        'metric': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'metric.log'),
            'formatter': 'verbose'
        },
        'hubspot': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'hubspot.log'),
            'formatter': 'verbose',
        },
        'ticket': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'ticket.log'),
            'formatter': 'verbose',
        },
        'referral': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'referral.log'),
            'formatter': 'verbose',
        },
        'badge': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'badge.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django_log': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'service': {
            'handlers': ['service'],
            'level': 'INFO',
            'propagate': True,
        },
        'segment': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['queries'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'registration_process': {
            'handlers': ['registration_process'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'files': {
            'handlers': ['files'],
            'level': 'INFO',
            'propagate': True,
        },
        'network': {
            'handlers': ['network'],
            'level': 'INFO',
            'propagate': True,
        },
        'user': {
            'handlers': ['users'],
            'level': 'INFO',
            'propagate': True,
        },
        'typeform': {
            'handlers': ['typeform_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'validator': {
            'handlers': ['validator'],
            'level': 'INFO',
            'propagate': True,
        },
        'social': {
            'handlers': ['social'],
            'level': 'INFO',
            'propagate': True,
        },
        'library': {
            'handlers': ['library'],
            'level': 'INFO',
            'propagate': True,
        },
        'accredible': {
            'handlers': ['accredible'],
            'level': 'INFO',
            'propagate': True,
        },
        'mail': {
            'handlers': ['mail'],
            'level': 'INFO',
            'propagate': True,
        },
        'zoom': {
            'handlers': ['zoom'],
            'level': 'INFO',
        },
        'metric': {
            'handlers': ['metric'],
            'level': 'INFO',
            'propagate': True,
        },
        'countries': {
            'handlers': ['countries'],
            'level': 'INFO',
            'propagate': True,
        },
        'hubspot': {
            'handlers': ['hubspot'],
            'level': 'INFO',
            'propagate': True,
        },
        'ticket': {
            'handlers': ['ticket'],
            'level': 'INFO',
            'propagate': True,
        },
        'referral': {
            'handlers': ['referral'],
            'level': 'INFO',
            'propagate': True,
        },
        'badge': {
            'handlers': ['badge'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
