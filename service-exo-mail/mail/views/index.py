from django.views.generic import TemplateView


class IndexView(TemplateView):
    http_method_names = ['get']
    template_name = 'pages/index.html'
