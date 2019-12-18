import yaml

from .accounts.accounts_loader import account_constructor
from .group.group_loader import group_constructor

# Custom constructors
yaml.Loader.add_constructor('!account', account_constructor)
yaml.Loader.add_constructor('!group', group_constructor)
