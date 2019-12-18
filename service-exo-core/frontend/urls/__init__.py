from django.conf.urls import url
from django.views.generic.base import TemplateView

from ..views import private


urlpatterns = [
    url(r'^demo-page/$', private.DemoPageView.as_view(), name='demo-page'),
]


urlpatterns += [
    url(r'^400/$', TemplateView.as_view(template_name='400.html')),
    url(r'^500/$', TemplateView.as_view(template_name='500.html')),
    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
]
