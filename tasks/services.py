import csv
import os
from asgiref.sync import async_to_sync
from django.core.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.exceptions import NotFound
from .models import CSVExport, Task
from .serializers import TaskUpdateSerializer
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Task
from channels.layers import get_channel_layer


class TaskService:

    @staticmethod
    def create_task(serializer, user):
        """
        Creates a task and triggers background email after DB commit
        """
        from .tasks import send_task_assignment_email

        task = serializer.save(created_by=user)
        transaction.on_commit(lambda: send_task_assignment_email.delay(task.id))
        log_user_activity(user=user, action="Created Task", task=task)

        return task


def mark_task_completed(task: Task):
    """
    Mark a task completed and trigger email notification to admins.
    """
    task.status = "completed"
    task.completed_at = timezone.now()
    task.save()

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


def generate_tasks_csv(file_name: str) -> str:
    media_root = settings.MEDIA_ROOT

    if not os.path.exists(media_root):
        os.makedirs(media_root)

    file_path = os.path.join(media_root, file_name)

    tasks = Task.objects.select_related("assigned_to").all()

    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(
            ["Title", "Status", "Priority", "Assigned User", "Created At", "Due Date"]
        )

        for task in tasks:
            writer.writerow(
                [
                    task.title,
                    task.status,
                    task.priority,
                    task.assigned_to.email if task.assigned_to else "",
                    task.created_at.strftime("%Y-%m-%d %H:%M"),
                    task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
                ]
            )

    return file_path


def broadcast_task_status_update(*, task_id: int, status: str):
    channel_layer = get_channel_layer()
    room_group_name = f"chat_room_{task_id}"

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "task.status",
            "task_id": task_id,
            "status": status,
        },
    )