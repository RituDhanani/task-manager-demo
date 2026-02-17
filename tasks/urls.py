from django.urls import path
from .views import CreateTaskAPIView, ListTaskAPIView

urlpatterns = [
    path('create-task/', CreateTaskAPIView.as_view(), name='create_task'),
    path('list-task/', ListTaskAPIView.as_view(), name='list_tasks'),

]
