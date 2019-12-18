from django.db.models import SET_NULL

from ..signals import set_null_signal


def SIGNAL_SET_NULL(collector, field, sub_objs, using):
    SET_NULL(collector, field, sub_objs, using)
    for obj in sub_objs:
        sender = obj.__class__
        set_null_signal.send(sender=sender, instance=obj)
