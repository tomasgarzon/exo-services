from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse
from django.db.models import Q

from utils.random import build_name

from ..models import Coupon
from ..forms.coupon import (
    CouponSearchListForm,
    CreateCouponForm,
    UpdateCouponForm)


class CouponListView(
        PermissionRequiredMixin,
        ListView):

    model = Coupon
    template_name = 'coupon/list.html'
    filter_form_class = CouponSearchListForm
    paginate_by = 50
    permission_required = 'exo_certification.list_coupon'

    def get(self, request, *args, **kwargs):
        self.form_filter = self.filter_form_class(request.GET)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all().order_by('-created')
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        if data.get('search'):
            q1 = Q(code__icontains=data.get('search'))
            q2 = Q(owner__short_name__icontains=data.get('search'))
            queryset = queryset.filter(q1 | q2).select_related('certification')
        return queryset.distinct()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_filter'] = self.form_filter
        return context


class CouponCreateView(CreateView):
    model = Coupon
    template_name = 'coupon/create.html'
    form_class = CreateCouponForm

    def get_form_kwargs(self, *args, **kwargs):
        response = super().get_form_kwargs(*args, **kwargs)
        response['user'] = self.request.user
        return response

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(**kwargs)
        initial['code'] = build_name(7)
        return initial

    def get_success_url(self):
        return reverse('tools:exo-certification:coupon-list')


class CouponUpdateView(UpdateView):
    model = Coupon
    template_name = 'coupon/create.html'
    form_class = UpdateCouponForm

    def get_form_kwargs(self, *args, **kwargs):
        response = super().get_form_kwargs(*args, **kwargs)
        response['user'] = self.request.user
        return response

    def get_success_url(self):
        return reverse('tools:exo-certification:coupon-list')


class CouponDetailView(DetailView):
    model = Coupon
    template_name = 'coupon/detail.html'
