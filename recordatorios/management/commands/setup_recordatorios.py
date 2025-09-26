"""
Comando para configurar el sistema de recordatorios con configuraciones por defecto
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recordatorios.models import (
    ConfiguracionRecordatorio, PlantillaRecordatorio,
    TipoRecordatorio, CanalNotificacion
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Configura el sistema de recordatorios con configuraciones por defecto'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación de configuraciones existentes'
        )
        parser.add_argument(
            '--templates',
            action='store_true',
            help='Crear también plantillas de ejemplo'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Configurando sistema de recordatorios...')
        )
        
        force = options['force']
        crear_templates = options['templates']
        
        # Crear configuraciones por defecto
        self._crear_configuraciones_por_defecto(force)
        
        # Crear plantillas de ejemplo si se solicita
        if crear_templates:
            self._crear_plantillas_ejemplo(force)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sistema de recordatorios configurado exitosamente!')
        )
    
    def _crear_configuraciones_por_defecto(self, force=False):
        """Crea configuraciones por defecto para tipos de recordatorios"""
        self.stdout.write('\n📋 Creando configuraciones por defecto...')
        
        configuraciones = [
            {
                'tipo': TipoRecordatorio.RESERVA_CONFIRMADA,
                'anticipacion_horas': 0,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 2,
                'delay_reintentos_minutos': 5
            },
            {
                'tipo': TipoRecordatorio.RECORDATORIO_DIA_ANTES,
                'anticipacion_horas': 24,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 3,
                'delay_reintentos_minutos': 15
            },
            {
                'tipo': TipoRecordatorio.RECORDATORIO_TRES_HORAS,
                'anticipacion_horas': 3,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp', 'sms'],
                'reintentos_maximos': 5,
                'delay_reintentos_minutos': 10
            },
            {
                'tipo': TipoRecordatorio.RESERVA_CANCELADA,
                'anticipacion_horas': 0,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 2,
                'delay_reintentos_minutos': 5
            },
            {
                'tipo': TipoRecordatorio.RESERVA_REAGENDADA,
                'anticipacion_horas': 0,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 2,
                'delay_reintentos_minutos': 5
            },
            {
                'tipo': TipoRecordatorio.SUSCRIPCION_RENOVACION,
                'anticipacion_horas': 168,  # 7 días
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 3,
                'delay_reintentos_minutos': 60
            },
            {
                'tipo': TipoRecordatorio.SUSCRIPCION_EXPIRADA,
                'anticipacion_horas': 0,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 2,
                'delay_reintentos_minutos': 30
            },
            {
                'tipo': TipoRecordatorio.INASISTENCIA,
                'anticipacion_horas': 0,
                'anticipacion_minutos': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 3,
                'delay_reintentos_minutos': 15
            }
        ]
        
        creadas = 0
        actualizadas = 0
        
        for config_data in configuraciones:
            try:
                config, created = ConfiguracionRecordatorio.objects.get_or_create(
                    tipo=config_data['tipo'],
                    defaults=config_data
                )
                
                if created:
                    creadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ {config_data['tipo']}: Configuración creada")
                    )
                elif force:
                    # Actualizar configuración existente
                    for key, value in config_data.items():
                        setattr(config, key, value)
                    config.save()
                    actualizadas += 1
                    self.stdout.write(
                        self.style.WARNING(f"  🔄 {config_data['tipo']}: Configuración actualizada")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ⏭️  {config_data['tipo']}: Ya existe")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ {config_data['tipo']}: Error - {e}")
                )
        
        self.stdout.write(f"\n📊 Resumen: {creadas} creadas, {actualizadas} actualizadas")
    
    def _crear_plantillas_ejemplo(self, force=False):
        """Crea plantillas de ejemplo para diferentes tipos de recordatorios"""
        self.stdout.write('\n📝 Creando plantillas de ejemplo...')
        
        # Obtener usuario admin para las plantillas
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
        except:
            admin_user = None
        
        plantillas = [
            {
                'nombre': 'Recordatorio Día Antes - Estándar',
                'tipo': TipoRecordatorio.RECORDATORIO_DIA_ANTES,
                'asunto': 'Recordatorio: Tu cita es mañana',
                'mensaje_texto': '''Hola {{ usuario }},

Te recordamos que tienes una cita mañana {{ fecha_formateada }} a las {{ hora_formateada }}.

Detalles:
- Negocio: {{ negocio }}
- Profesional: {{ profesional }}
- Servicio: {{ reserva.servicio }}

¡Te esperamos!

Saludos,
Equipo {{ negocio }}''',
                'mensaje_html': '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #333;">Recordatorio de Cita</h2>
    
    <p>Hola <strong>{{ usuario }}</strong>,</p>
    
    <p>Te recordamos que tienes una cita <strong>mañana {{ fecha_formateada }}</strong> a las <strong>{{ hora_formateada }}</strong>.</p>
    
    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0;">Detalles de la Cita:</h3>
        <ul>
            <li><strong>Negocio:</strong> {{ negocio }}</li>
            <li><strong>Profesional:</strong> {{ profesional }}</li>
            <li><strong>Servicio:</strong> {{ reserva.servicio }}</li>
        </ul>
    </div>
    
    <p style="color: #666;">¡Te esperamos!</p>
    
    <p>Saludos,<br>
    <strong>Equipo {{ negocio }}</strong></p>
</div>''',
                'variables_disponibles': ['usuario', 'fecha_formateada', 'hora_formateada', 'negocio', 'profesional', 'reserva']
            },
            {
                'nombre': 'Recordatorio 3 Horas - Urgente',
                'tipo': TipoRecordatorio.RECORDATORIO_TRES_HORAS,
                'asunto': 'URGENTE: Tu cita es en 3 horas',
                'mensaje_texto': '''URGENTE: {{ usuario }}

Tu cita es en 3 HORAS ({{ fecha_formateada }} a las {{ hora_formateada }}).

📍 {{ negocio }}
👨‍⚕️ {{ profesional }}
💇‍♀️ {{ reserva.servicio }}

¡No olvides tu cita!''',
                'mensaje_html': '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #ff4444; color: white; padding: 20px; border-radius: 5px; text-align: center;">
        <h1 style="margin: 0;">🚨 URGENTE 🚨</h1>
        <h2 style="margin: 10px 0;">Tu cita es en 3 HORAS</h2>
    </div>
    
    <div style="padding: 20px;">
        <p><strong>{{ usuario }}</strong>, tu cita es:</p>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #856404;">📅 {{ fecha_formateada }} a las {{ hora_formateada }}</h3>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <p><strong>📍 Negocio:</strong> {{ negocio }}</p>
            <p><strong>👨‍⚕️ Profesional:</strong> {{ profesional }}</p>
            <p><strong>💇‍♀️ Servicio:</strong> {{ reserva.servicio }}</p>
        </div>
        
        <p style="text-align: center; margin-top: 20px; font-size: 18px; font-weight: bold;">
            ¡No olvides tu cita!
        </p>
    </div>
</div>''',
                'variables_disponibles': ['usuario', 'fecha_formateada', 'hora_formateada', 'negocio', 'profesional', 'reserva']
            },
            {
                'nombre': 'Confirmación de Reserva',
                'tipo': TipoRecordatorio.RESERVA_CONFIRMADA,
                'asunto': '✅ Reserva confirmada - {{ negocio }}',
                'mensaje_texto': '''¡Reserva confirmada!

Hola {{ usuario }},

Tu reserva ha sido confirmada exitosamente:

📅 Fecha: {{ fecha_formateada }}
🕐 Hora: {{ hora_formateada }}
📍 Negocio: {{ negocio }}
👨‍⚕️ Profesional: {{ profesional }}
💇‍♀️ Servicio: {{ reserva.servicio }}

Te enviaremos recordatorios antes de tu cita.

¡Gracias por elegirnos!''',
                'mensaje_html': '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; text-align: center; border: 1px solid #c3e6cb;">
        <h1 style="margin: 0;">✅ Reserva Confirmada</h1>
    </div>
    
    <div style="padding: 20px;">
        <p>¡Hola <strong>{{ usuario }}</strong>!</p>
        
        <p>Tu reserva ha sido confirmada exitosamente:</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <span style="font-size: 20px; margin-right: 10px;">📅</span>
                <strong>Fecha:</strong> {{ fecha_formateada }}
            </div>
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <span style="font-size: 20px; margin-right: 10px;">🕐</span>
                <strong>Hora:</strong> {{ hora_formateada }}
            </div>
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <span style="font-size: 20px; margin-right: 10px;">📍</span>
                <strong>Negocio:</strong> {{ negocio }}
            </div>
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <span style="font-size: 20px; margin-right: 10px;">👨‍⚕️</span>
                <strong>Profesional:</strong> {{ profesional }}
            </div>
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <span style="font-size: 20px; margin-right: 10px;">💇‍♀️</span>
                <strong>Servicio:</strong> {{ reserva.servicio }}
            </div>
        </div>
        
        <p><em>Te enviaremos recordatorios antes de tu cita.</em></p>
        
        <p style="text-align: center; margin-top: 20px; font-size: 18px; color: #28a745;">
            ¡Gracias por elegirnos!
        </p>
    </div>
</div>''',
                'variables_disponibles': ['usuario', 'fecha_formateada', 'hora_formateada', 'negocio', 'profesional', 'reserva']
            }
        ]
        
        creadas = 0
        actualizadas = 0
        
        for plantilla_data in plantillas:
            try:
                plantilla, created = PlantillaRecordatorio.objects.get_or_create(
                    nombre=plantilla_data['nombre'],
                    defaults={
                        **plantilla_data,
                        'creado_por': admin_user
                    }
                )
                
                if created:
                    creadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ {plantilla_data['nombre']}: Plantilla creada")
                    )
                elif force:
                    # Actualizar plantilla existente
                    for key, value in plantilla_data.items():
                        if key != 'creado_por':
                            setattr(plantilla, key, value)
                    plantilla.save()
                    actualizadas += 1
                    self.stdout.write(
                        self.style.WARNING(f"  🔄 {plantilla_data['nombre']}: Plantilla actualizada")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ⏭️  {plantilla_data['nombre']}: Ya existe")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ {plantilla_data['nombre']}: Error - {e}")
                )
        
        self.stdout.write(f"\n📊 Resumen plantillas: {creadas} creadas, {actualizadas} actualizadas")
    
    def _mostrar_resumen_final(self):
        """Muestra resumen final de la configuración"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE')
        self.stdout.write('='*60)
        
        # Estadísticas
        total_configs = ConfiguracionRecordatorio.objects.count()
        total_plantillas = PlantillaRecordatorio.objects.count()
        
        self.stdout.write(f"📋 Configuraciones creadas: {total_configs}")
        self.stdout.write(f"📝 Plantillas disponibles: {total_plantillas}")
        
        self.stdout.write('\n🚀 Próximos pasos:')
        self.stdout.write('1. Ejecutar migraciones: python manage.py migrate')
        self.stdout.write('2. Crear superusuario: python manage.py createsuperuser')
        self.stdout.write('3. Acceder al admin: /admin/')
        self.stdout.write('4. Probar recordatorios: python manage.py procesar_recordatorios --dry-run')
        
        self.stdout.write('\n📚 Documentación: SISTEMA_RECORDATORIOS_README.md')
        self.stdout.write('='*60)
