def answer_post_delete_handler(sender, instance, *args, **kwargs):
    instance.post.remove_reply(instance)
