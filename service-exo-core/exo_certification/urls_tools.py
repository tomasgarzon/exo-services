from django.conf.urls import url
from .views import coupon

app_name = 'exo-certification'


urlpatterns = [
    url(
        r'^list/$',
        coupon.CouponListView.as_view(),
        name='coupon-list'),
    url(
        r'^create/$',
        coupon.CouponCreateView.as_view(),
        name='coupon-create'),
    url(
        r'^update/(?P<pk>\d+)/$',
        coupon.CouponUpdateView.as_view(),
        name='coupon-update'),
    url(
        r'^detail/(?P<pk>\d+)/$',
        coupon.CouponDetailView.as_view(),
        name='coupon-detail'),
]
