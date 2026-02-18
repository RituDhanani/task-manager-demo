from django.db import transaction
from .tasks import send_task_assignment_email

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

