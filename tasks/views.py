from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskCreateSerializer, TaskListSerializer
from .permissions import IsAdminOrManager
from rest_framework.generics import ListAPIView
from .models import Task

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
