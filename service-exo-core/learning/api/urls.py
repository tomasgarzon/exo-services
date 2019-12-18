from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns


from .views import (
    autocomplete_tag,
    training_session
)


app_name = 'learning'

urlpatterns = [
    # Autocomplete
    url(
        r'^tags-autocomplete/$',
        autocomplete_tag.TagAutocomplete.as_view(create_field='name'),
        name='tags-autocomplete',
    ),
    url(
        r'^training-session/$',
        training_session.TrainingSessionListView.as_view(),
        name='training-session-list',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
