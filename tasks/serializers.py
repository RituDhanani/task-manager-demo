from rest_framework import serializers
from django.contrib.auth import get_user_model

from tasks.validators import validate_task_attachment
from .models import Task, TaskAttachment

User = get_user_model()


class TaskCreateSerializer(serializers.ModelSerializer):

    assigned_to_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "status",
            "assigned_to_email",
            "due_date",
        ]

    def validate_assigned_to_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        return value

    def create(self, validated_data):
        email = validated_data.pop("assigned_to_email")
        user = User.objects.get(email=email)

        task = Task.objects.create(
            assigned_to=user,
            **validated_data
        )

        return task




class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = serializers.EmailField(source="assigned_to.email")
    created_by = serializers.EmailField(source="created_by.email")
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "created_by",
            "created_at",
            "updated_at",
        ]


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "status",
        ]


class TaskAttachmentSerializer(serializers.ModelSerializer):

    file = serializers.FileField(validators=[validate_task_attachment])
    class Meta:
        model = TaskAttachment
        fields = ["id", "task", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]