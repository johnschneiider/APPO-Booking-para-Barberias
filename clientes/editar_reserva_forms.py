"""
Formularios para editar reservas
"""

from django import forms
from django.utils import timezone
from .models import Reserva
from negocios.models import Negocio, ServicioNegocio
from profesionales.models import Profesional

class EditarReservaForm(forms.ModelForm):
    """
    Formulario para editar una reserva existente
    """
    
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'servicio', 'profesional', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'servicio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'profesional': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            # Filtrar servicios y profesionales del negocio específico
            negocio = self.instance.peluquero
            self.fields['servicio'].queryset = ServicioNegocio.objects.filter(negocio=negocio)
            self.fields['profesional'].queryset = Profesional.objects.filter(negocio=negocio)
            
            # Establecer fecha mínima como hoy
            self.fields['fecha'].widget.attrs['min'] = timezone.now().date().isoformat()
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now().date():
            raise forms.ValidationError('No puedes reagendar para una fecha en el pasado.')
        return fecha
    
    def clean_hora_inicio(self):
        hora_inicio = self.cleaned_data.get('hora_inicio')
        fecha = self.cleaned_data.get('fecha')
        
        if fecha and hora_inicio:
            # Verificar que no sea en el pasado
            ahora = timezone.now()
            if fecha == ahora.date() and hora_inicio <= ahora.time():
                raise forms.ValidationError('No puedes reagendar para una hora en el pasado.')
        
        return hora_inicio
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        if fecha and hora_inicio and hora_fin:
            # Verificar que hora_fin sea después de hora_inicio
            if hora_fin <= hora_inicio:
                raise forms.ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
        
        return cleaned_data

