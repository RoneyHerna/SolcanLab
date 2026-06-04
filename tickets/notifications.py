from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timesince import timesince

from .models import TicketNotification


NOTIFICATION_PREVIEW_LIMIT = 5


def get_user_notifications(user):
    if not user.is_authenticated:
        return TicketNotification.objects.none()

    return TicketNotification.objects.select_related(
        'ticket',
        'recipient',
    ).filter(
        recipient=user,
    )[:NOTIFICATION_PREVIEW_LIMIT]


def get_unread_notification_count(user):
    if not user.is_authenticated:
        return 0

    return TicketNotification.objects.filter(
        recipient=user,
        is_read=False,
    ).count()


def serialize_notification(notification):
    return {
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'is_read': notification.is_read,
        'url': f'/tickets/notifications/{notification.id}/open/',
        'time_label': f'hace {timesince(notification.created_at)}',
    }


def get_user_notification_summary(user):
    notifications = get_user_notifications(user)

    return {
        'unread_count': get_unread_notification_count(user),
        'notifications': [
            serialize_notification(notification)
            for notification in notifications
        ],
    }


def notify_admins_ticket_created(ticket):
    if ticket.created_by.role != 'client':
        return

    user_model = get_user_model()
    admin_ids = user_model.objects.filter(
        role='admin',
        is_active=True,
    ).values_list('id', flat=True)

    notifications = [
        TicketNotification(
            recipient_id=admin_id,
            ticket=ticket,
            notification_type='ticket_created',
            title=f'Nuevo ticket #{ticket.id}',
            message=f'Registrado por {ticket.created_by.username}: {ticket.title}.',
        )
        for admin_id in admin_ids
    ]

    TicketNotification.objects.bulk_create(notifications)


def mark_user_notifications_as_read(user):
    if not user.is_authenticated:
        return

    TicketNotification.objects.filter(
        recipient=user,
        is_read=False,
    ).update(
        is_read=True,
        read_at=timezone.now(),
    )
