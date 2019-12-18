import os

MAIL_FROM_EMAIL = 'OpenExO <hello@openexo.com>'
MAIL_REPLY_TO = 'support@openexo.com'
MAIL_NETWORK_LIST_MAIL_GROUP = 'Network List Email'
MAIL_SUPPORT_LIST_MAIL_GROUP = 'Support List Email'
MAIL_FINANCIAL_LIST_MAIL_GROUP = 'Financial List Email'

# Sendgrid settings
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
