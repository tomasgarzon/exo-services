import os

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')

SERVICES = [
    '/opportunities',
    '/conversations',
    '/mails',
    '/exo-auth',
    '/projects',
    '/events',
    '/exq',
    '/jobs',
    '/companies',
    ''  # exolever
]
