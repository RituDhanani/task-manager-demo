from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskCreateSerializer
from .permissions import IsAdminOrManager


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

