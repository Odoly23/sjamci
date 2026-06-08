from .models import Notification

def send_notification(sender, receiver, title, message, notif_type, link=None):
    return Notification.objects.create(
        sender=sender,
        receiver=receiver,
        title=title,
        message=message,
        notif_type=notif_type,
        link=link or ""
    )