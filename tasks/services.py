from django.core.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.exceptions import NotFound
from .models import Task
from .serializers import TaskUpdateSerializer
from .tasks import notify_admin_task_completed
from django.utils import timezone

class TaskService:

    @staticmethod
    def create_task(serializer, user):
        """
        Creates a task and triggers background email after DB commit
        """
        from django.db import transaction
        from .tasks import send_task_assignment_email

        # Save task with correct user
        task = serializer.save(created_by=user)

        # Trigger celery task only after successful DB commit
        transaction.on_commit(
            lambda: send_task_assignment_email.delay(task.id)
        )

        return task

def mark_task_completed(task: Task):
    """
    Mark a task completed and trigger email notification to admins.
    """
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save()

    # Trigger background Celery task after DB commit
    transaction.on_commit(lambda: notify_admin_task_completed.delay(task.id))
