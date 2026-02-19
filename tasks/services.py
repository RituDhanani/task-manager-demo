from django.core.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.exceptions import NotFound
from .models import Task
from .serializers import TaskUpdateSerializer
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


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
        transaction.on_commit(lambda: send_task_assignment_email.delay(task.id))

        # Log activity (AFTER commit)
        log_user_activity(user=user, action="Created Task", task=task)

        return task


def mark_task_completed(task: Task):
    """
    Mark a task completed and trigger email notification to admins.
    """
    task.status = "completed"
    task.completed_at = timezone.now()
    task.save()

    # Trigger background Celery task after DB commit
    from .tasks import notify_admin_task_completed

    transaction.on_commit(lambda: notify_admin_task_completed.delay(task.id))


def get_tasks_due_within_24_hours():
    now = timezone.now()
    next_24 = now + timedelta(hours=24)

    return Task.objects.filter(due_date__range=(now, next_24), reminder_sent=False)


def send_due_reminder_email(task):
    subject = f"Reminder: Task '{task.title}' is due soon"
    message = f"Your task '{task.title}' is due on {task.due_date}."

    send_mail(
        subject,
        message,
        None,
        [task.assigned_to.email],
    )

    task.reminder_sent = True
    task.save()


def log_user_activity(user, action, task=None):

    from .tasks import create_activity_log

    transaction.on_commit(
        lambda: create_activity_log.delay(user.id, action, task.id if task else None)
    )
