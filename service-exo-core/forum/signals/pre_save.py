from utils.func_utils import parse_urls


def topic_pre_save_handler(sender, instance, *args, **kwargs):
    instance.description = parse_urls(instance.description)


def answer_pre_save_handler(sender, instance, *args, **kwargs):
    instance.comment = parse_urls(instance.comment)
