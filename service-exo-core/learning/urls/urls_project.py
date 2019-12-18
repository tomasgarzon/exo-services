from django.conf.urls import url

from ..views import microlearning


app_name = 'learning'

urlpatterns = [
    url(
        r'^microlearning-step/(?P<pk>\d+)/$',
        microlearning.EditMicrolearningStepView.as_view(),
        name='step',
    ),
]
