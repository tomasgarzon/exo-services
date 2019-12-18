from django.urls import path

from .views import country, language

app_name = 'core'

urlpatterns = [
    path('languages/', language.LanguageListView.as_view()),
    path('country/', country.CountryListView.as_view()),
]
