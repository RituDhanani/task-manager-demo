from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import (TaskCreateSerializer, TaskListSerializer, 
                          TaskUpdateSerializer)
from .permissions import IsAdminOrManager
from rest_framework.generics import (ListAPIView, RetrieveAPIView, UpdateAPIView,
                                    DestroyAPIView)
from .models import Task
from rest_framework.exceptions import PermissionDenied


#create task apiview
class CreateTaskAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def post(self, request):
        serializer = TaskCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Task created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#list task apiview
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


#update task apiview
class UpdateTaskAPIView(UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        task = super().get_object()
        user = self.request.user

        # Manager → Can update only tasks they created
        if user.role == "Manager" and task.created_by == user:
            return task

        # Member → Can update only tasks assigned to them
        if user.role == "Member" and task.assigned_to == user:
            return task

        raise PermissionDenied("You do not have permission to update this task.")
    

#delete task apiview
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