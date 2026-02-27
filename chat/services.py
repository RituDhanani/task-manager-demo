from chat.models import ChatRoom
from tasks.models import Task


def user_can_join_room(*, user, room_id: int) -> bool:
    if user.is_superuser:
        return True

    try:
        room = ChatRoom.objects.select_related("task").get(id=room_id)
    except ChatRoom.DoesNotExist:
        return False

    if not room.task:
        return False

    task: Task = room.task

    if task.assigned_to_id == user.id:
        return True

    if task.created_by_id == user.id:
        return True

    return False