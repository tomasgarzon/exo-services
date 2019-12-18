from django.conf.urls import url, include

from ..views import project_view, qa_session, media_list
from ..views.consultant import list
from ..views.steps import step_list, step_edit, step_detail

app_name = 'project'

urlpatterns = [
    url(r'^team/', include('team.urls', namespace='team')),
    url(r'^validations/', include('validation.urls', namespace='validations')),
    url(r'^assignment/', include('assignment.urls', namespace='assignment')),
    url(r'^consultants/$', list.ConsultantListView.as_view(), name='consultants'),
    url(r'^steps/$', step_list.StepListView.as_view(), name='steps'),
    url(r'^steps/edit/(?P<pk>\d+)/$', step_edit.StepEditView.as_view(), name='steps-edit'),
    url(r'^steps/edit-period/(?P<pk>\d+)/$', step_edit.StepEditPeriodView.as_view(), name='steps-period-edit'),
    url(r'^steps/detail/(?P<pk>\d+)/$', step_detail.StepDetailView.as_view(), name='steps-detail'),
    url(r'^steps/export/(?P<pk>\d+)/$', step_detail.StepExportView.as_view(), name='step-export-yml'),
    url(r'^steps/import/(?P<pk>\d+)/$', step_detail.StepImportYMLView.as_view(), name='step-import-yml'),
    url(r'^swarm-session/$', qa_session.QASessionListView.as_view(), name='swarm-session'),
    url(r'^swarm-session/add/$', qa_session.QASessionAddView.as_view(), name='swarm-session-add'),
    url(r'^swarm-session/edit/(?P<pk>\d+)/$', qa_session.QASessionEditView.as_view(), name='swarm-session-edit'),
    url(r'^swarm-session/delete/(?P<pk>\d+)/$', qa_session.QASessionDeleteView.as_view(), name='swarm-session-delete'),
    url(r'^swarm-session/detail/(?P<pk>\d+)/$', qa_session.QASessionDetailView.as_view(), name='swarm-session-detail'),
    url(r'^files/', include('files.urls.urls_project', namespace='file')),
    url(r'^settings/$', project_view.ProjectSettingsView.as_view(), name='settings'),
    url(r'^learning/', include('learning.urls.urls_project', namespace='learning')),
    url(r'^media/(?P<resource_pk>\d+)/delete/$',
        media_list.MediaLibraryProjectResourceDeleteView.as_view(), name='remove-media'),
    url(r'^media/add/$', media_list.MediaLibraryAddResourcesView.as_view(), name='add-media'),
    url(r'^media/populate/$', media_list.MediaLibraryProjectPopulateView.as_view(), name='populate-media'),
    url(r'^media/$', media_list.MediaLibraryProjectResourcesView.as_view(), name='media'),
    url(r'^$', project_view.ProjectGeneralView.as_view(), name='dashboard'),
]
