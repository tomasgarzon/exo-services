from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from mail.models import Message

from ..forms.message import MessageFilterForm, MessageAddressesForm
from ..engine import send_email


class InboxMixinView(LoginRequiredMixin):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['section'] = 'inbox'
        return context


class InboxMessageListView(InboxMixinView, ListView, FormView):
    model = Message
    queryset = Message.objects.all()
    form_class = MessageFilterForm
    template_name = 'pages/inbox.html'
    paginate_by = 20
    ordering = ['-created']

    def get_queryset(self):
        subject = self.request.GET.get('subject', None)
        email = self.request.GET.get('email', None)
        if subject:
            q1 = Q(subject__icontains=subject)
            self.queryset = self.queryset.filter(q1)
        if email:
            self.queryset = self.queryset.filter(to_email__icontains=email)
        return super().get_queryset()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        form = self.get_form()
        form.fields['subject'].initial = self.request.GET.get('subject')
        form.fields['email'].initial = self.request.GET.get('email')
        context['form'] = form
        return context


class InboxMessageDetailView(InboxMixinView, DetailView, FormView):
    model = Message
    template_name = 'pages/inbox_message.html'
    form_class = MessageAddressesForm
    pk = None

    def get_success_url(self):
        return reverse_lazy('mail:inbox-message', kwargs={'pk': self.pk})

    def form_valid(self, form):
        message = self.get_object()
        self.pk = message.pk
        to_addresses = self.request.POST.get('addresses').split(',')
        if to_addresses:
            send_email(message, to_addresses)
            messages.success(self.request, 'Email successfully queued. Please, check the status below!')
        return super().form_valid(form)
