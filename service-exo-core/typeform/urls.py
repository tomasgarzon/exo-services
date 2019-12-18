from django.urls import path, include


app_name = 'typeform'

urlpatterns = [
    path('', include('typeform_feedback.urls')),
]
