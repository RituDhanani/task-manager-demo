from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import ActivityLog, Task
from django.contrib.auth import get_user_model
import logging
from django.utils import timezone
from .services import get_tasks_due_within_24_hours, send_due_reminder_email

User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_task_assignment_email(self, task_id):
    """
    Background email sending when task assigned
    """
    try:
        task = Task.objects.get(id=task_id)

        if not task.assigned_to:
            return "No user assigned"

        subject = "New Task Assigned"
        message = f"""
        Hello {task.assigned_to.email},

        You have been assigned a new task.

        Title: {task.title}
        Description: {task.description}
        Priority: {task.priority}
        Status: {task.status}

        Please login to system to view details.
        """

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [task.assigned_to.email],
            fail_silently=False,
        )

        return "Email sent successfully"

    except Exception as e:
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3)
def notify_admin_task_completed(self, task_id):
    try:
        task = Task.objects.get(id=task_id)
        admins = User.objects.filter(is_staff=True)

        subject = f"Task Completed: {task.title}"
        message = f"The task '{task.title}' assigned to {task.assigned_to} has been marked as completed."
        from_email = None  # Uses DEFAULT_FROM_EMAIL

        recipient_list = [admin.email for admin in admins if admin.email]

        if recipient_list:
            send_mail(subject, message, from_email, recipient_list)

        print(
            f"[Activity Log] Task '{task.title}' marked completed. Emails sent to admins: {recipient_list}"
        )

    except Task.DoesNotExist:
        print(f"Task with id {task_id} does not exist")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_due_task_reminders(self):
    try:
        tasks = get_tasks_due_within_24_hours()

        for task in tasks:
            send_due_reminder_email(task)

        print("Due task reminders processed.")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def create_activity_log(self, user_id, action, task_id=None):
    try:
        user = User.objects.get(id=user_id)

        # DO NOT crash if task is deleted
        task = None
        if task_id:
            task = Task.objects.filter(id=task_id).first()

        ActivityLog.objects.create(user=user, action=action, task=task)

        print(f"[ActivityLog Created] {action}")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
