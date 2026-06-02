from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from tickets.forms import TicketExportFilterForm
from tickets.models import Ticket


CLIENT_TICKETS_PER_PAGE = 9

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


def build_priority_bars(priority_counts):
    max_priority_count = max(*priority_counts.values(), 1)

    return [
        {
            'label': label,
            'count': priority_counts[priority],
            'color': color,
            'percent': round((priority_counts[priority] / max_priority_count) * 100),
        }
        for label, priority, color in PRIORITY_CHART_CONFIG
    ]


def build_donut_gradient(percentages):
    progress_stop = percentages['open'] + percentages['progress']

    return (
        f"conic-gradient(#2563eb 0 {percentages['open']}%, "
        f"#8a3ffc {percentages['open']}% {progress_stop}%, "
        f"#22c55e {progress_stop}% 100%)"
    )


def get_visible_tickets(request, tickets):
    if request.user.role != 'client':
        return tickets, None

    paginator = Paginator(tickets, CLIENT_TICKETS_PER_PAGE)
    ticket_page = paginator.get_page(request.GET.get('page'))

    return ticket_page, ticket_page


def build_dashboard_context(request):
    user = request.user
    user_model = get_user_model()
    tickets = get_ticket_queryset(user)
    visible_tickets, ticket_page = get_visible_tickets(request, tickets)
    status_counts = get_status_counts(tickets)
    status_percentages = get_status_percentages(status_counts)
    priority_counts = get_priority_counts(tickets)

    return {
        'tickets': visible_tickets,
        'ticket_page': ticket_page,
        'export_form': TicketExportFilterForm() if user.role == 'admin' else None,
        'total_tickets': status_counts['total'],
        'open_tickets': status_counts['open'],
        'progress_tickets': status_counts['progress'],
        'closed_tickets': status_counts['closed'],
        'client_count': user_model.objects.filter(role='client').count() if user.role == 'admin' else None,
        'recent_tickets': tickets[:5],
        'priority_bars': build_priority_bars(priority_counts),
        'donut_gradient': build_donut_gradient(status_percentages),
        'open_percent': status_percentages['open'],
        'progress_percent': status_percentages['progress'],
        'closed_percent': status_percentages['closed'],
    }


@login_required
def dashboard(request):
    return render(
        request,
        'dashboard/index.html',
        build_dashboard_context(request)
    )