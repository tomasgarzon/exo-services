from .define import post_save_resource_signal
from .resource import post_save_resource


def setup_signals():
    post_save_resource_signal.connect(post_save_resource)
