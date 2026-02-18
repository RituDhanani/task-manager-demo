from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Task


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

