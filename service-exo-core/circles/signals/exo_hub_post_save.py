from django.conf import settings

from ..models import Circle
from ..circle_helper import get_certification_role


def exo_hub_post_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        circle = Circle.objects.create(
            code=instance._type,
            type=settings.CIRCLES_CH_TYPE_CERTIFIED,
            name=instance.get_circle_name(),
            hub=instance)
        circle.certification_required = get_certification_role(circle.slug)
        circle.save()
