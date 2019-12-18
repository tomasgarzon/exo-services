from consultant.models import Consultant

from ..signals_define import post_save_consultant_signal
from ..signals_define import projects_ecosystem_changed
from .update_member import update_ecosystem_handler
from .consultant import post_save_consultant


def setup_signals():
    post_save_consultant_signal.connect(post_save_consultant, sender=Consultant)
    projects_ecosystem_changed.connect(update_ecosystem_handler)
