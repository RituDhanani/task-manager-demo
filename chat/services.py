from chat.models import ChatRoom, Message
from tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


def create_message(*, room_id: int, user_id: int, content: str) -> Message:
  
    room = ChatRoom.objects.get(id=room_id)
    user = User.objects.get(id=user_id)

    return Message.objects.create(
        room=room,
        sender=user,
        content=content,
    )


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