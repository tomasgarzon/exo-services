from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect

from ..models import UserBadge, UserBadgeItem
from ..forms import UserBadgeJobItemForm
from ..conf import settings
from .mixins import UserBadgeSectionViewMixin


class UserBadgeDetailView(UserBadgeSectionViewMixin, DetailView):
    model = UserBadge
    template_name = 'badge/user_badge_detail.html'


class UserBadgeJobItemUpdateView(UserBadgeSectionViewMixin, UpdateView):
    model = UserBadgeItem
    form_class = UserBadgeJobItemForm
    template_name = 'badge/user_badge_form.html'
    success_message = 'Badge was updated successfully.'
    success_url = reverse_lazy('tools:badge:list')

    def form_valid(self, form):
        super().form_valid(form)
        description = 'item-{}'.format(self.object.pk)

        self.object.user_badge.create_log(
            user_from=self.request.user,
            verb=settings.BADGE_ACTION_LOG_UPDATE,
            description=description)

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class UserBadgeItemDeleteView(UserBadgeSectionViewMixin, DeleteView):
    model = UserBadgeItem
    template_name = 'badge/user_badge_item_confirm_delete.html'
    success_message = 'Badge was removed successfully.'
    success_url = reverse_lazy('tools:badge:list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        description = 'item {}'.format(self.object.pk)
        messages.success(self.request, self.success_message)

        response = super().delete(request, *args, **kwargs)

        self.object.user_badge.create_log(
            user_from=self.request.user,
            verb=settings.BADGE_ACTION_LOG_DELETE,
            description=description)

        return response


class UserBadgeDeleteView(UserBadgeSectionViewMixin, DeleteView):
    model = UserBadge
    template_name = 'badge/user_badge_confirm_delete.html'
    success_message = 'Badge was removed successfully.'
    success_url = reverse_lazy('tools:badge:list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        description = self.object.pk
        messages.success(self.request, self.success_message)

        response = super().delete(request, *args, **kwargs)

        self.object.create_log(
            user_from=self.request.user,
            verb=settings.BADGE_ACTION_LOG_DELETE,
            description=description)

        return response
