import yaml

from django.utils import timezone

from datetime import timedelta

from .accounts.accounts_loader import account_constructor
from .projects.project_loader import project_constructor
from .team.team_loader import team_constructor


def timedelta_constructor(loader, node):
    item = loader.construct_scalar(node)
    num, typ = item[:-1], item[-1].lower()
    num = int(num)
    tmdt = None
    if typ == 'd':
        tmdt = timedelta(days=num)
    elif typ == 'h':
        tmdt = timedelta(seconds=num * 3600)
    elif typ == 'w':
        tmdt = timedelta(days=num * 7)
    elif typ == 'm':
        tmdt = timedelta(seconds=num * 60)
    elif typ == 's':
        tmdt = timedelta(seconds=num)
    return timezone.now() + tmdt


# Base
yaml.Loader.add_constructor('!timedelta', timedelta_constructor)

# Custom constructors
yaml.Loader.add_constructor('!account', account_constructor)
yaml.Loader.add_constructor('!project', project_constructor)
yaml.Loader.add_constructor('!team', team_constructor)
