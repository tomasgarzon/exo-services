from django.conf import settings
from djproxy.urls import generate_routes

urlpatterns = generate_routes(getattr(settings, 'LOCAL_DOCKER_PROXY', {}))
