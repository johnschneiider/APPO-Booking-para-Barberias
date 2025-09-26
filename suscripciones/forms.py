from django import forms
from django.core.exceptions import ValidationError
from .models import PlanSuscripcion, BeneficioSuscripcion, Suscripcion

class PlanSuscripcionForm(forms.ModelForm):
    """Formulario para crear y editar planes de suscripción"""
    
    class Meta:
        model = PlanSuscripcion
        fields = [
            'nombre', 'descripcion', 'precio_mensual', 'duracion_meses',
            'max_suscripciones', 'activo', 'destacado', 'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Plan Premium Mensual'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe qué incluye tu plan y por qué es atractivo...'
            }),
            'precio_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '50000'
            }),
            'duracion_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '12',
                'placeholder': '1'
            }),
            'max_suscripciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Deja en blanco para ilimitado'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'destacado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'nombre': 'Nombre del Plan',
            'descripcion': 'Descripción',
            'precio_mensual': 'Precio Mensual ($)',
            'duracion_meses': 'Duración (meses)',
            'max_suscripciones': 'Máximo de Suscripciones',
            'activo': 'Plan Activo',
            'destacado': 'Plan Destacado',
            'imagen': 'Imagen del Plan'
        }
        help_texts = {
            'nombre': 'Un nombre atractivo y descriptivo para tu plan',
            'descripcion': 'Explica claramente qué beneficios incluye',
            'precio_mensual': 'Precio en pesos colombianos',
            'duracion_meses': 'Número de meses que dura la suscripción',
            'max_suscripciones': 'Límite de clientes que pueden suscribirse (opcional)',
            'activo': 'Los planes inactivos no aparecen para los clientes',
            'destacado': 'Los planes destacados aparecen primero en las búsquedas',
            'imagen': 'Imagen representativa del plan (opcional)'
        }
    
    def clean_precio_mensual(self):
        precio = self.cleaned_data['precio_mensual']
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor a 0')
        return precio
    
    def clean_duracion_meses(self):
        duracion = self.cleaned_data['duracion_meses']
        if duracion < 1 or duracion > 12:
            raise ValidationError('La duración debe estar entre 1 y 12 meses')
        return duracion
    
    def clean_max_suscripciones(self):
        max_suscripciones = self.cleaned_data['max_suscripciones']
        if max_suscripciones is not None and max_suscripciones <= 0:
            raise ValidationError('El máximo de suscripciones debe ser mayor a 0')
        return max_suscripciones

class BeneficioSuscripcionForm(forms.ModelForm):
    """Formulario para crear y editar beneficios de suscripción"""
    
    class Meta:
        model = BeneficioSuscripcion
        fields = ['nombre', 'descripcion', 'tipo_beneficio', 'valor', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Descuento en servicios'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el beneficio en detalle...'
            }),
            'tipo_beneficio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 20% o 5000'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre del Beneficio',
            'descripcion': 'Descripción',
            'tipo_beneficio': 'Tipo de Beneficio',
            'valor': 'Valor del Beneficio',
            'activo': 'Beneficio Activo'
        }
        help_texts = {
            'nombre': 'Nombre corto y descriptivo del beneficio',
            'descripcion': 'Explica cómo funciona el beneficio',
            'tipo_beneficio': 'Categoría del beneficio',
            'valor': 'Porcentaje, monto fijo o descripción del valor',
            'activo': 'Los beneficios inactivos no se muestran a los clientes'
        }

class SuscripcionForm(forms.ModelForm):
    """Formulario para crear suscripciones (uso interno)"""
    
    class Meta:
        model = Suscripcion
        fields = ['cliente', 'plan', 'fecha_inicio', 'fecha_vencimiento', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'plan': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'cliente': 'Cliente',
            'plan': 'Plan de Suscripción',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'estado': 'Estado'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        if fecha_inicio and fecha_vencimiento:
            if fecha_vencimiento <= fecha_inicio:
                raise ValidationError('La fecha de vencimiento debe ser posterior a la fecha de inicio')
        
        return cleaned_data

class SuscripcionClienteForm(forms.Form):
    """Formulario para que los clientes se suscriban"""
    
    plan_id = forms.IntegerField(widget=forms.HiddenInput())
    renovacion_automatica = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Renovación Automática',
        help_text='Renovar automáticamente al vencer'
    )
    notificar_antes_renovacion = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Notificar Antes de Renovar',
        help_text='Recibir notificación 7 días antes del vencimiento'
    )
    acepto_terminos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Acepto los términos y condiciones',
        help_text='Debes aceptar los términos para continuar'
    )
    
    def __init__(self, *args, **kwargs):
        negocio = kwargs.pop('negocio', None)
        super().__init__(*args, **kwargs)
        
        if negocio:
            # Personalizar el formulario según el negocio
            self.fields['acepto_terminos'].help_text = f'Acepto los términos y condiciones de {negocio.nombre}'
    
    def clean_acepto_terminos(self):
        acepto = self.cleaned_data.get('acepto_terminos')
        if not acepto:
            raise ValidationError('Debes aceptar los términos y condiciones para continuar')
        return acepto

class CancelarSuscripcionForm(forms.Form):
    """Formulario para cancelar suscripciones"""
    
    motivo = forms.ChoiceField(
        choices=[
            ('', 'Selecciona un motivo'),
            ('precio', 'El precio es muy alto'),
            ('servicios', 'Los servicios no cumplen mis expectativas'),
            ('atencion', 'Mala atención al cliente'),
            ('ubicacion', 'Cambié de ubicación'),
            ('otro', 'Otro motivo')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Motivo de Cancelación',
        help_text='Ayúdanos a mejorar seleccionando el motivo'
    )
    
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Comentarios adicionales (opcional)...'
        }),
        label='Comentarios Adicionales',
        help_text='Comparte más detalles sobre tu experiencia'
    )
    
    confirmar_cancelacion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Confirmo que quiero cancelar mi suscripción',
        help_text='Esta acción no se puede deshacer'
    )
    
    def clean_confirmar_cancelacion(self):
        confirmar = self.cleaned_data.get('confirmar_cancelacion')
        if not confirmar:
            raise ValidationError('Debes confirmar la cancelación para continuar')
        return confirmar

class CambiarPlanForm(forms.Form):
    """Formulario para cambiar de plan"""
    
    nuevo_plan = forms.ModelChoiceField(
        queryset=PlanSuscripcion.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Nuevo Plan',
        help_text='Selecciona el plan al que quieres cambiar'
    )
    
    fecha_cambio = forms.ChoiceField(
        choices=[
            ('inmediato', 'Cambio inmediato'),
            ('proximo_ciclo', 'Próximo ciclo de facturación')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Fecha del Cambio',
        help_text='Cuándo quieres que se aplique el cambio'
    )
    
    confirmar_cambio = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Confirmo el cambio de plan',
        help_text='Entiendo que el cambio se aplicará según la fecha seleccionada'
    )
    
    def __init__(self, *args, **kwargs):
        negocio = kwargs.pop('negocio', None)
        suscripcion_actual = kwargs.pop('suscripcion_actual', None)
        super().__init__(*args, **kwargs)
        
        if negocio:
            # Filtrar planes disponibles (excluyendo el actual)
            planes_disponibles = PlanSuscripcion.objects.filter(
                negocio=negocio,
                activo=True
            ).exclude(id=suscripcion_actual.plan.id if suscripcion_actual else 0)
            
            self.fields['nuevo_plan'].queryset = planes_disponibles
            self.fields['nuevo_plan'].label = f'Nuevo Plan de {negocio.nombre}'
    
    def clean_confirmar_cambio(self):
        confirmar = self.cleaned_data.get('confirmar_cambio')
        if not confirmar:
            raise ValidationError('Debes confirmar el cambio de plan para continuar')
        return confirmar

class BuscarPlanesForm(forms.Form):
    """Formulario para buscar planes disponibles"""
    
    categoria = forms.ChoiceField(
        choices=[
            ('', 'Todas las categorías'),
            ('peluqueria', 'Peluquería'),
            ('estetica', 'Estética'),
            ('spa', 'Spa'),
            ('belleza', 'Belleza'),
            ('bienestar', 'Bienestar')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ubicacion = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ciudad o barrio'
        })
    )
    
    precio_min = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio mínimo'
        })
    )
    
    precio_max = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio máximo'
        })
    )
    
    duracion = forms.ChoiceField(
        choices=[
            ('', 'Cualquier duración'),
            ('1', '1 mes'),
            ('3', '3 meses'),
            ('6', '6 meses'),
            ('12', '12 meses')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        precio_min = cleaned_data.get('precio_min')
        precio_max = cleaned_data.get('precio_max')
        
        if precio_min and precio_max and precio_min > precio_max:
            raise ValidationError('El precio mínimo no puede ser mayor al precio máximo')
        
        return cleaned_data

class FiltrosSuscripcionesForm(forms.Form):
    """Formulario para filtrar suscripciones"""
    
    estado = forms.ChoiceField(
        choices=[
            ('', 'Todos los estados'),
            ('activa', 'Activas'),
            ('vencida', 'Vencidas'),
            ('proxima_vencer', 'Próximas a Vencer'),
            ('cancelada', 'Canceladas')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    plan = forms.ModelChoiceField(
        queryset=PlanSuscripcion.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Todos los planes'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        negocio = kwargs.pop('negocio', None)
        super().__init__(*args, **kwargs)
        
        if negocio:
            self.fields['plan'].queryset = PlanSuscripcion.objects.filter(negocio=negocio, activo=True)
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise ValidationError('La fecha desde no puede ser posterior a la fecha hasta')
        
        return cleaned_data
