from django.urls import path

from .views import badge_list, badge_add, badge_detail

app_name = 'badge'

urlpatterns = [
    path('list/', badge_list.UserBadgeListView.as_view(), name='list'),
    path('add-activity-job/', badge_add.UserBadgeActivityAddView.as_view(), name='add-activity-job'),
    path('update-job-item/<str:pk>/', badge_detail.UserBadgeJobItemUpdateView.as_view(), name='update-job-item'),
    path('detail/<str:pk>/', badge_detail.UserBadgeDetailView.as_view(), name='detail'),
    path('delete-item/<str:pk>/', badge_detail.UserBadgeItemDeleteView.as_view(), name='delete-item'),
    path('delete/<str:pk>/', badge_detail.UserBadgeDeleteView.as_view(), name='delete'),
]
