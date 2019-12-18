def slug_edit(sender, instance, previous_value, new_value, tag_model, *args, **kwargs):
    tag_model.tags.tag_model.objects.filter(name=previous_value).update(name=new_value)
