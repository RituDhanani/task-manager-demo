from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from tasks.tasks import notify_admin_task_completed
from .serializers import (TaskAttachmentSerializer, TaskCreateSerializer, TaskListSerializer,
                          TaskUpdateSerializer)
from .permissions import IsAdminOrManager
from rest_framework.generics import (ListAPIView, RetrieveAPIView, UpdateAPIView,
                                    DestroyAPIView,
                )
from .models import Task, TaskAttachment
from rest_framework.exceptions import PermissionDenied
from .services import  TaskService, log_user_activity
from django.shortcuts import get_object_or_404
from django.db import transaction
from .tasks import send_due_task_reminders, heavy_csv_export_task
from rest_framework.permissions import IsAdminUser


# create task apiview
class CreateTaskAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def post(self, request):
        serializer = TaskCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            TaskService.create_task(serializer, request.user)

            return Response(
                {"message": "Task created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# list task apiview
class ListTaskAPIView(ListAPIView):

    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_param = self.request.query_params.get("status")

        if user.role == "Admin":
            queryset = Task.objects.all()

        elif user.role == "Manager":
            queryset = Task.objects.filter(created_by=user)

        elif user.role == "Member":
            queryset = Task.objects.filter(assigned_to=user)

        else:
            return Task.objects.none()

        # Apply status filter if provided
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset.order_by("-created_at")


# retrieve task apiview
class RetrieveTaskAPIView(RetrieveAPIView):

    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        task = super().get_object()
        user = self.request.user

        # Admin → Can access any task
        if user.role == "Admin":
            return task

        # Manager → Only tasks created by them
        if user.role == "Manager" and task.created_by == user:
            return task

        # Member → Only tasks assigned to them
        if user.role == "Member" and task.assigned_to == user:
            return task

        raise PermissionDenied("You do not have permission to access this task.")


# update task apiview
class UpdateTaskAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            task = Task.objects.get(id=id)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found"}, status=404)
        user = request.user
        if not (user.is_staff or task.assigned_to == user):
            return Response({"detail": "Not allowed"}, status=403)

        old_status = task.status

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()
        # Trigger Celery if status changed to completed
        if old_status != "Completed" and updated_task.status == "Completed":
            transaction.on_commit(
                lambda: notify_admin_task_completed.delay(updated_task.id)
            )

        log_user_activity(
            user=user,
            action="Updated Task",
            task=updated_task
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


# delete task apiview
class DeleteTaskAPIView(DestroyAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        task = super().get_object()
        user = self.request.user

        # Only Admin can delete
        if user.role == "Admin":
            return task
        raise PermissionDenied("Only Admin can delete tasks.")
    

    def perform_destroy(self, instance):
        log_user_activity(
            user=self.request.user,
            action="Deleted Task",
            task=instance
        )

        instance.delete()

#trigger reminder apiview
class TriggerReminderAPIView(APIView):

    def post(self, request):
        send_due_task_reminders.delay()

        return Response(
            {"message": "Reminder task triggered successfully"},
            status=status.HTTP_200_OK,
        )


#CSV export apiview
class HeavyCSVExportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        admin_email = request.user.email

        # Ensure task runs only after DB transaction is committed
        transaction.on_commit(lambda: heavy_csv_export_task.delay(admin_email))

        return Response({
            "message": "Your export is being prepared. You will receive an email shortly."
        })
    
#task attachment apiview
class TaskAttachmentUploadView(generics.CreateAPIView):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)