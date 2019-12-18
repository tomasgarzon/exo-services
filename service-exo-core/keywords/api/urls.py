from django.conf.urls import url

from .views import dal_autocomplete


app_name = 'keywords'

urlpatterns = [
    url(
        r'^autocomplete/$',
        dal_autocomplete.KeywordAutocomplete.as_view(),
        name='keywords-autocomplete',
    ),
]
