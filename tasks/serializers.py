from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()


class TaskCreateSerializer(serializers.ModelSerializer):

    assigned_to = serializers.EmailField(write_only=True)

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "status",
            "assigned_to"
        ]

    def create(self, validated_data):
        assigned_email = validated_data.pop("assigned_to")

        try:
            assigned_user = User.objects.get(email=assigned_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"assigned_to": "User with this email does not exist"}
            )

        task = Task.objects.create(
            assigned_to=assigned_user,
            created_by=self.context["request"].user,
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
