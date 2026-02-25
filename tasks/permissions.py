from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["Admin", "Manager"]
        )
    
class CanAccessAttachment(BasePermission):
    """
    Allow access if:
    - Manager
    - Admin
    - Assigned user of task
    - Creator of task
    """

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if hasattr(user, "role") and user.role == "Manager":
            return True

        if obj.task.assigned_to == user:
            return True

        if obj.task.created_by == user:
            return True

        return False