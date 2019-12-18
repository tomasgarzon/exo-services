import yaml

from .accounts.accounts_loader import account_constructor
from .survey.survey_loader import survey_reference_constructor

# Custom constructors
yaml.Loader.add_constructor('!account', account_constructor)
yaml.Loader.add_constructor('!survey', survey_reference_constructor)
