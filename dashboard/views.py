from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from tickets.selectors import (
    PRIORITY_CHART_CONFIG,
    get_priority_counts,
    get_status_counts,
    get_status_percentages,
    get_ticket_queryset,
)


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


def build_dashboard_context(request):
    user_model = get_user_model()
    tickets = get_ticket_queryset(request.user)
    status_counts = get_status_counts(tickets)
    status_percentages = get_status_percentages(status_counts)
    priority_counts = get_priority_counts(tickets)

    return {
        'total_tickets': status_counts['total'],
        'open_tickets': status_counts['open'],
        'progress_tickets': status_counts['progress'],
        'closed_tickets': status_counts['closed'],
        'client_count': user_model.objects.filter(role='client').count(),
        'recent_tickets': tickets[:4],
        'priority_bars': build_priority_bars(priority_counts),
        'donut_gradient': build_donut_gradient(status_percentages),
        'open_percent': status_percentages['open'],
        'progress_percent': status_percentages['progress'],
        'closed_percent': status_percentages['closed'],
    }


@login_required
def dashboard(request):
    if request.user.role == 'client':
        return redirect('/tickets/')

    return render(
        request,
        'dashboard/index.html',
        build_dashboard_context(request),
    )
