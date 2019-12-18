from relation.signals_define import (
    add_user_exo_hub,
    remove_user_exo_hub,
)
from .user_in_hub import add_user_in_hub_handler, remove_user_in_hub_handler


def setup_signals():
    add_user_exo_hub.connect(
        add_user_in_hub_handler)
    remove_user_exo_hub.connect(
        remove_user_in_hub_handler)
