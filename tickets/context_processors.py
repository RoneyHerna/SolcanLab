from .notifications import (
    get_unread_notification_count,
    get_user_notifications,
)


def ticket_notifications(request):
    return {
        'dashboard_notifications': get_user_notifications(request.user),
        'dashboard_unread_notifications': get_unread_notification_count(
            request.user
        ),
    }
