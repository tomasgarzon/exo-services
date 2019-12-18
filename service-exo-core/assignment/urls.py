from django.conf.urls import url

from .views import list_assignment

app_name = 'assignment'

urlpatterns = [
    url(
        r'^assignment-step/$',
        list_assignment.AssignmentStepListView.as_view(),
        name='list-assignment-steps',
    ),
]
