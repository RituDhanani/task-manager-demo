from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskCreateSerializer, TaskListSerializer, TaskUpdateSerializer
from .permissions import IsAdminOrManager
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
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

        # Admin → See all tasks
        if user.role == "Admin":
            return Task.objects.all().order_by("-created_at")

        # Manager → See tasks created by them
        if user.role == "Manager":
            return Task.objects.filter(
                created_by=user
            ).order_by("-created_at")

        # Member → See tasks assigned to them
        if user.role == "Member":
            return Task.objects.filter(
                assigned_to=user
            ).order_by("-created_at")

        return Task.objects.none()


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


#update tsk apiview
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
