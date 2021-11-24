from data.models import EmailStorage


def write_messages_to_db(email: str, messages: dict):
    new_user = EmailStorage()
    new_user.user_email = email
    new_user.messages_json = messages

    return new_user.save()
