from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.http.response import HttpResponseRedirect

from ..models import UserBadge
from ..forms import UserBadgeActivityForm
from ..helpers import update_or_create_badge
from .mixins import UserBadgeSectionViewMixin


class UserBadgeAddViewMixin(UserBadgeSectionViewMixin, CreateView):
    model = UserBadge
    template_name = 'badge/user_badge_form.html'
    success_message = 'Badge was created successfully.'
    success_url = reverse_lazy('tools:badge:list')

    def _get_user(self, form):
        return get_user_model().objects.filter(
            emailaddress__email=form.cleaned_data.get('email'),
        ).first()

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class UserBadgeActivityAddView(UserBadgeAddViewMixin):
    form_class = UserBadgeActivityForm

    def form_valid(self, form):
        badge = form.cleaned_data.get('badge')
        description = form.data.get('comment')

        self.object = update_or_create_badge(
            user_from=self.request.user,
            user_to=self._get_user(form),
            code=badge.code,
            category=badge.category,
            description=description)

        return super().form_valid(form)
