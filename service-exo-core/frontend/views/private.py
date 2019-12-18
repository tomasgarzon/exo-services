from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class DemoPageView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/demo_page.html'
