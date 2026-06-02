from django.urls import path
from . import views


urlpatterns = [

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
