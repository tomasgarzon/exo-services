from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title=settings.BRAND_NAME + ' Documentation',
        default_version='v1',
        description='Test description',
        terms_of_service='https://www.openexo.com/privacy-policy',
        contact=openapi.Contact(email='support@openexo.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)
