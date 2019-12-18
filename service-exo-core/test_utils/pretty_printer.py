# Standard Library
import json

# Project Library
from bson import json_util


def format_dict(data):
    return json.dumps(data, default=json_util.default, indent=4)
