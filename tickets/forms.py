from pathlib import Path

from django import forms

from .models import Ticket, TicketNote


MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024
ALLOWED_ATTACHMENT_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}

MONTH_CHOICES = (
    ('', 'Mes'),
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre'),
)


def validate_attachment(file):
    if not file:
        return

    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise forms.ValidationError(
            'Solo se permiten archivos JPG, PNG, WEBP o PDF.'
        )

    if file.size > MAX_ATTACHMENT_SIZE:
        raise forms.ValidationError(
            'El archivo no puede ser mayor a 5 MB.'
        )


class TicketForm(forms.ModelForm):
    attachment = forms.FileField(
        label='Adjuntar archivo',
        required=False,
        validators=[validate_attachment],
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'priority')
        labels = {
            'title': 'Titulo',
            'description': 'Descripcion',
            'priority': 'Prioridad',
        }
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Titulo del problema',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'placeholder': 'Describe el problema',
                }
            ),
            'priority': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
        }


class TicketNoteForm(forms.ModelForm):
    attachment = forms.FileField(
        label='Adjuntar archivo',
        required=False,
        validators=[validate_attachment],
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    class Meta:
        model = TicketNote
        fields = ('message',)
        labels = {
            'message': 'Nota tecnica',
        }
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Agregar nota tecnica...',
                }
            ),
        }


class TicketExportFilterForm(forms.Form):
    day = forms.IntegerField(
        label='Día',
        required=False,
        min_value=1,
        max_value=31,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Día',
            }
        ),
    )
    month = forms.ChoiceField(
        label='Mes',
        required=False,
        choices=MONTH_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
    )
    year = forms.IntegerField(
        label='Año',
        required=False,
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Año',
            }
        ),
    )
