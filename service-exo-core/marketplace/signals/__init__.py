from django.apps import apps
from django.db.models.signals import post_save

from .service_request import post_save_service_request


def setup_signals():
    ServiceRequest = apps.get_model(app_label='marketplace', model_name='ServiceRequest')
    post_save.connect(post_save_service_request, sender=ServiceRequest)
