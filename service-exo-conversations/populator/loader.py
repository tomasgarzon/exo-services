import yaml

from .accounts.accounts_loader import account_constructor

# Custom constructors
yaml.Loader.add_constructor('!account', account_constructor)
