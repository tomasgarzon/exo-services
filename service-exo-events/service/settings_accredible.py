import os
from .local import ACCREDIBLE_SANDBOX  # noqa

ACCREDIBLE_PDF_HOST = 'https://pdf.credential.net'

if ACCREDIBLE_SANDBOX:
    ACCREDIBLE_API_KEY = os.environ.get('ACCREDIBLE_API_KEY', '')
    ACCREDIBLE_SERVER_URL = 'https://sandbox.api.accredible.com/v1/'
    ACCREDIBLE_DESIGN = {
        'workshop': '102126',
    }
else:
    ACCREDIBLE_API_KEY = os.environ.get('ACCREDIBLE_API_KEY', '')
    ACCREDIBLE_SERVER_URL = 'https://api.accredible.com/v1/'
    ACCREDIBLE_DESIGN = {
        'workshop': '107484',
    }

CERTIFICATION_CH_GROUP_WORKSHOP = 'workshop'

CERTIFICATION_CH_GROUP_CH_TYPE = (
    (CERTIFICATION_CH_GROUP_WORKSHOP, 'Workshop'),
)

ACCREDIBLE_USER_NAME_HANDLER = 'utils.accredible.get_user_name'
ACCREDIBLE_USER_EMAIL_HANDLER = 'utils.accredible.get_user_email'
