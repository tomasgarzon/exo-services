from django.urls import path

from .views import templates, mailbox, public, index
from .handlers import mail_handler

app_name = 'mail'

urlpatterns = [
    path('inbox/<int:pk>/', mailbox.InboxMessageDetailView.as_view(), name='inbox-message'),
    path('inbox/', mailbox.InboxMessageListView.as_view(), name='inbox'),
    path('templates/<str:mail_view_name>/'.format(view_name='|'.join(mail_handler._registry.keys())),
         templates.switch_view, name='mail-view'),
    path('templates/', templates.TemplatesListView.as_view(), name='templates'),
    path('templates/public/<str:hash>', public.public_view, name='public'),
    path('', index.IndexView.as_view(), name='index'),
]
