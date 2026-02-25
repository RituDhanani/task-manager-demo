from django.conf import settings
from rest_framework import serializers


def validate_profile_image(file):
    # Validate file type
    if file.content_type not in settings.ALLOWED_PROFILE_IMAGE_TYPES:
        raise serializers.ValidationError(
            "Only JPEG and PNG files are allowed."
        )

    # Validate file size
    if file.size > settings.MAX_PROFILE_IMAGE_SIZE:
        raise serializers.ValidationError(
            "File size must be less than 2MB."
        )

    return file