from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.ticket_list,
        name='ticket_list'
    ),

    path(
        'create/',
        views.create_ticket,
        name='create_ticket'
    ),

    path(
        'export/',
        views.export_tickets,
        name='export_tickets'
    ),

    path(
        'notifications/<int:notification_id>/open/',
        views.open_notification,
        name='open_notification'
    ),

    path(
        'notifications/summary/',
        views.notification_summary,
        name='notification_summary'
    ),

    path(
        'notifications/read/',
        views.mark_notifications_read,
        name='mark_notifications_read'
    ),

     path(
        'take/<int:ticket_id>/',
        views.take_ticket,
        name='take_ticket'
    ),

    path(
        'close/<int:ticket_id>/',
        views.close_ticket,
        name='close_ticket'
    ),

    path(
    'detail/<int:ticket_id>/',
    views.ticket_detail,
    name='ticket_detail'
    ),

    path(
        'add-note/<int:ticket_id>/',
        views.add_note,
        name='add_note'
    ),

]
