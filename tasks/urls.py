from django.urls import path
from .views import (ActivityReportPDFView, CreateTaskAPIView, ListTaskAPIView, RetrieveTaskAPIView, 
                    TaskAttachmentUploadView, TaskDetailPDFView, UpdateTaskAPIView, DeleteTaskAPIView, 
                    TriggerReminderAPIView, HeavyCSVExportView, SecureAttachmentDownloadView,
                    TaskReportPDFView)

urlpatterns = [
    path('create-task/', CreateTaskAPIView.as_view(), name='create_task'),
    path('list-task/', ListTaskAPIView.as_view(), name='list_tasks'),
    path('retrieve-task/<int:id>/', RetrieveTaskAPIView.as_view(), name='retrieve_task'),
    path('update-task/<int:id>/', UpdateTaskAPIView.as_view(), name='update_task'),
    path('delete-task/<int:id>/', DeleteTaskAPIView.as_view(), name='delete_task'),
    path("trigger-reminder/", TriggerReminderAPIView.as_view(), name="trigger_reminder"),
    path("export-tasks/", HeavyCSVExportView.as_view(), name="export-tasks"),
    path("attachments-upload/", TaskAttachmentUploadView.as_view(), name="upload-attachment"),
    path("attachments/<int:id>/download/", SecureAttachmentDownloadView.as_view(), name="download-attachment"),
    path("task-report-pdf/", TaskReportPDFView.as_view(), name="task-report-pdf"),
    path("task-detail-pdf/<int:task_id>/", TaskDetailPDFView.as_view(), name="task-detail-pdf"),
    path("activity-report-pdf/", ActivityReportPDFView.as_view(), name="activity-report-pdf"),

]
