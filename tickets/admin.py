from django.contrib import admin

from .models import Ticket, TicketNotification


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'status',
        'priority',
        'elaboration_date',
        'created_by',
        'assigned_to',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'elaboration_date',
    )

    search_fields = (
        'title',
        'description',
    )


@admin.register(TicketNotification)
class TicketNotificationAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'recipient',
        'ticket',
        'is_read',
        'created_at',
    )

    list_filter = (
        'is_read',
        'notification_type',
        'created_at',
    )

    search_fields = (
        'title',
        'message',
        'ticket__title',
        'recipient__username',
    )
