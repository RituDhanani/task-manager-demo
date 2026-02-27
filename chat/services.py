def create_message(*, room_id: int, user_id: int, content: str):
    
    from django.contrib.auth import get_user_model
    from chat.models import ChatRoom, Message

    User = get_user_model()

    room = ChatRoom.objects.get(id=room_id)
    user = User.objects.get(id=user_id)

    return Message.objects.create(
        room=room,
        sender=user,
        content=content,
    )