from django.urls import path
from .views import CreateTaskAPIView

urlpatterns = [
    path('create-task/', CreateTaskAPIView.as_view(), name='create_task'),
]
