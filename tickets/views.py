from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .exports import build_ticket_export_workbook
from .forms import TicketExportFilterForm, TicketForm, TicketNoteForm
from .models import (
    NoteAttachment,
    Ticket,
    TicketAttachment,
    TicketNote,
    TicketNotification,
)
from .notifications import (
    get_user_notification_summary,
    mark_user_notifications_as_read,
    notify_admins_ticket_created,
)
from .selectors import get_status_counts, get_ticket_queryset


TICKETS_PER_PAGE = 9


def create_ticket_attachment(ticket, attachment):
    if attachment:
        TicketAttachment.objects.create(
            ticket=ticket,
            file=attachment,
        )


def create_note_attachment(note, attachment):
    if attachment:
        NoteAttachment.objects.create(
            note=note,
            file=attachment,
        )


def user_can_view_ticket(user, ticket):
    return user.role != 'client' or ticket.created_by == user


def get_ticket_notes(user, ticket):
    return ticket.notes.select_related('user').prefetch_related(
        'attachments'
    ).order_by('-created_at')


def get_ticket_detail_context(ticket, user, note_form=None):
    return {
        'ticket': ticket,
        'notes': get_ticket_notes(user, ticket),
        'attachments': ticket.attachments.all(),
        'note_form': note_form or TicketNoteForm(),
    }


def get_ticket_list_context(request):
    tickets = get_ticket_queryset(request.user)
    ticket_page = Paginator(tickets, TICKETS_PER_PAGE).get_page(
        request.GET.get('page')
    )
    status_counts = get_status_counts(tickets)

    return {
        'tickets': ticket_page,
        'ticket_page': ticket_page,
        'export_form': TicketExportFilterForm() if request.user.role == 'admin' else None,
        'total_tickets': status_counts['total'],
        'open_tickets': status_counts['open'],
    }


def get_export_tickets(filters):
    tickets = Ticket.objects.select_related(
        'created_by',
        'assigned_to',
    ).order_by('-elaboration_date', '-created_at')

    if filters.get('day'):
        tickets = tickets.filter(elaboration_date__day=filters['day'])

    if filters.get('month'):
        tickets = tickets.filter(elaboration_date__month=int(filters['month']))

    if filters.get('year'):
        tickets = tickets.filter(elaboration_date__year=filters['year'])

    return tickets


def build_export_filename(filters):
    filename_parts = ['tickets']

    if filters.get('year'):
        filename_parts.append(str(filters['year']))

    if filters.get('month'):
        filename_parts.append(str(filters['month']).zfill(2))

    if filters.get('day'):
        filename_parts.append(str(filters['day']).zfill(2))

    return '_'.join(filename_parts) + '.xlsx'


@login_required
def ticket_list(request):
    return render(
        request,
        'tickets/index.html',
        get_ticket_list_context(request),
    )


@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            create_ticket_attachment(
                ticket,
                form.cleaned_data.get('attachment'),
            )
            notify_admins_ticket_created(ticket)

            return redirect('/tickets/')
    else:
        form = TicketForm()

    return render(
        request,
        'tickets/create.html',
        {
            'form': form,
        }
    )


@login_required
def take_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user.role == 'admin' and ticket.assigned_to is None:
        ticket.assigned_to = request.user
        ticket.status = 'progress'
        ticket.save()

    return redirect('/tickets/')


@login_required
def close_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user.role == 'admin' and ticket.assigned_to == request.user:
        ticket.status = 'closed'
        ticket.save()

    return redirect('/tickets/')


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not user_can_view_ticket(request.user, ticket):
        return redirect('/tickets/')

    return render(
        request,
        'tickets/detail.html',
        get_ticket_detail_context(ticket, request.user),
    )


@login_required
def add_note(request, ticket_id):
    if request.user.role != 'admin':
        return redirect('/tickets/')

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = TicketNoteForm(request.POST, request.FILES)

        if form.is_valid():
            note = form.save(commit=False)
            note.ticket = ticket
            note.user = request.user
            note.save()

            create_note_attachment(
                note,
                form.cleaned_data.get('attachment'),
            )
        else:
            return render(
                request,
                'tickets/detail.html',
                get_ticket_detail_context(ticket, request.user, form),
            )

    return redirect(f'/tickets/detail/{ticket.id}/')


@login_required
def export_tickets(request):
    if request.user.role != 'admin':
        return redirect('/tickets/')

    form = TicketExportFilterForm(request.GET)

    if not form.is_valid():
        return redirect('/tickets/')

    filters = form.cleaned_data
    tickets = get_export_tickets(filters)
    output = build_ticket_export_workbook(tickets)
    filename = build_export_filename(filters)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def open_notification(request, notification_id):
    notification = get_object_or_404(
        TicketNotification,
        id=notification_id,
        recipient=request.user,
    )
    notification.mark_as_read()

    if notification.ticket and user_can_view_ticket(
        request.user,
        notification.ticket,
    ):
        return redirect(f'/tickets/detail/{notification.ticket.id}/')

    return redirect('/tickets/')


@login_required
@require_GET
def notification_summary(request):
    return JsonResponse(get_user_notification_summary(request.user))


@login_required
@require_POST
def mark_notifications_read(request):
    mark_user_notifications_as_read(request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(get_user_notification_summary(request.user))

    return redirect(request.META.get('HTTP_REFERER', '/tickets/'))
