from django.views.generic import TemplateView

from ..handlers import mail_handler


class TemplatesListView(TemplateView):
    http_method_names = ['get']
    template_name = 'pages/templates.html'

    def get_context_data(self, **kwargs):
        context = super(TemplatesListView, self).get_context_data(**kwargs)
        mail_views = [
            {
                'subject': mail_handler._registry.get(mail_view_key).subject or '* No subject',
                'elem': mail_view_key,
                'section': mail_handler._registry.get(mail_view_key).section or 'Uncategorized',
            }
            for mail_view_key in mail_handler._registry.keys()
        ]
        mail_views = sorted(mail_views, key=lambda view: view['section'])
        context['mail_views'] = mail_views
        context['section'] = 'templates'
        return context


def switch_view(request, mail_view_name):
    return mail_handler._registry[mail_view_name].__class__.as_view()(request)
