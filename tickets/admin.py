from django.contrib import admin

from .models import Ticket


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
