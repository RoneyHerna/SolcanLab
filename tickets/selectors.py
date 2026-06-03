from .models import Ticket


PRIORITY_CHART_CONFIG = (
    ('Alta', 'high', '#ef4444'),
    ('Media', 'medium', '#f6b500'),
    ('Baja', 'low', '#22c55e'),
)


def get_ticket_queryset(user):
    tickets = Ticket.objects.select_related(
        'created_by',
        'assigned_to',
    ).order_by('-created_at')

    if user.role == 'client':
        return tickets.filter(created_by=user)

    return tickets


def get_status_counts(tickets):
    return {
        'total': tickets.count(),
        'open': tickets.filter(status='open').count(),
        'progress': tickets.filter(status='progress').count(),
        'closed': tickets.filter(status='closed').count(),
    }


def get_status_percentages(counts):
    total = counts['total']

    if not total:
        return {
            'open': 0,
            'progress': 0,
            'closed': 0,
        }

    open_percent = round((counts['open'] / total) * 100, 1)
    progress_percent = round((counts['progress'] / total) * 100, 1)

    return {
        'open': open_percent,
        'progress': progress_percent,
        'closed': max(0, round(100 - open_percent - progress_percent, 1)),
    }


def get_priority_counts(tickets):
    return {
        priority: tickets.filter(priority=priority).count()
        for _, priority, _ in PRIORITY_CHART_CONFIG
    }
