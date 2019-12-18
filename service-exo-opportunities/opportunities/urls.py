from django.urls import path

from .views import applicant_sow

app_name = 'opportunities'

urlpatterns = [
    path('<int:pk>/', applicant_sow.ApplicantSowPDF.as_view(), name='download-sow-pdf'),
]
