from django.conf import settings
from rest_framework.exceptions import ValidationError


def validate_task_attachment(file):

    # File size validation
    if file.size > settings.MAX_TASK_ATTACHMENT_SIZE:
        raise ValidationError("File size exceeds 5MB limit.")

    # File type validation
    if file.content_type not in settings.ALLOWED_TASK_ATTACHMENT_TYPES:
        raise ValidationError("Unsupported file type. Allowed: PDF, JPG, PNG, DOCX.")