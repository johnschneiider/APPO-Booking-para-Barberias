"""
Comando para procesar recordatorios pendientes
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from recordatorios.services import servicio_recordatorios
from recordatorios.models import Recordatorio, EstadoRecordatorio
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Procesa recordatorios pendientes que están listos para enviar'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula el procesamiento sin enviar realmente'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Límite de recordatorios a procesar'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza el procesamiento de recordatorios vencidos'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando procesamiento de recordatorios...')
        )
        
        # Configuración
        dry_run = options['dry_run']
        limit = options['limit']
        force = options['force']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO SIMULACIÓN - No se enviarán recordatorios')
            )
        
        # Obtener recordatorios pendientes
        recordatorios = self._obtener_recordatorios_pendientes(force, limit)
        
        if not recordatorios:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay recordatorios pendientes para procesar')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'📧 Procesando {len(recordatorios)} recordatorios...')
        )
        
        # Estadísticas
        estadisticas = {
            'procesados': 0,
            'enviados': 0,
            'fallidos': 0,
            'reintentos': 0,
            'errores': 0
        }
        
        # Procesar cada recordatorio
        for recordatorio in recordatorios:
            try:
                if verbose:
                    self.stdout.write(f'  📝 Procesando: {recordatorio.id} - {recordatorio.tipo}')
                
                if dry_run:
                    # Simular procesamiento
                    resultado = self._simular_procesamiento(recordatorio)
                else:
                    # Procesamiento real
                    resultado = servicio_recordatorios._procesar_recordatorio(recordatorio)
                
                estadisticas['procesados'] += 1
                
                if resultado['enviado']:
                    estadisticas['enviados'] += 1
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✅ Enviado exitosamente')
                        )
                elif resultado['fallido']:
                    estadisticas['fallidos'] += 1
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f'    ❌ Falló el envío')
                        )
                elif resultado['reintento']:
                    estadisticas['reintentos'] += 1
                    if verbose:
                        self.stdout.write(
                            self.style.WARNING(f'    🔄 Programado para reintento')
                        )
                        
            except Exception as e:
                estadisticas['errores'] += 1
                logger.error(f"Error procesando recordatorio {recordatorio.id}: {e}")
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f'    💥 Error: {e}')
                    )
        
        # Mostrar resumen
        self._mostrar_resumen(estadisticas, dry_run)
        
        # Logs adicionales
        if not dry_run:
            logger.info(f"Recordatorios procesados: {estadisticas}")
    
    def _obtener_recordatorios_pendientes(self, force: bool, limit: int = None):
        """Obtiene recordatorios pendientes listos para procesar"""
        ahora = timezone.now()
        
        queryset = Recordatorio.objects.filter(
            estado=EstadoRecordatorio.PENDIENTE
        ).order_by('prioridad', 'fecha_programada')
        
        if not force:
            # Solo recordatorios que están listos para enviar
            queryset = queryset.filter(fecha_programada__lte=ahora)
        
        if limit:
            queryset = queryset[:limit]
        
        return list(queryset)
    
    def _simular_procesamiento(self, recordatorio):
        """Simula el procesamiento de un recordatorio"""
        # Simular resultado exitoso en la mayoría de casos
        import random
        
        # 80% de éxito, 15% fallido, 5% reintento
        rand = random.random()
        
        if rand < 0.8:
            return {'enviado': True, 'fallido': False, 'reintento': False}
        elif rand < 0.95:
            return {'enviado': False, 'fallido': True, 'reintento': False}
        else:
            return {'enviado': False, 'fallido': False, 'reintento': True}
    
    def _mostrar_resumen(self, estadisticas: dict, dry_run: bool):
        """Muestra el resumen del procesamiento"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMEN DEL PROCESAMIENTO')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write('⚠️  MODO SIMULACIÓN')
            self.stdout.write('')
        
        self.stdout.write(f"📝 Total procesados: {estadisticas['procesados']}")
        self.stdout.write(f"✅ Enviados exitosamente: {estadisticas['enviados']}")
        self.stdout.write(f"❌ Fallidos: {estadisticas['fallidos']}")
        self.stdout.write(f"🔄 Programados para reintento: {estadisticas['reintentos']}")
        self.stdout.write(f"💥 Errores: {estadisticas['errores']}")
        
        if estadisticas['procesados'] > 0:
            tasa_exito = (estadisticas['enviados'] / estadisticas['procesados']) * 100
            self.stdout.write(f"📈 Tasa de éxito: {tasa_exito:.1f}%")
        
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Este fue un procesamiento simulado')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Procesamiento completado')
            )
    
    def _mostrar_estadisticas_generales(self):
        """Muestra estadísticas generales del sistema"""
        total_recordatorios = Recordatorio.objects.count()
        pendientes = Recordatorio.objects.filter(estado=EstadoRecordatorio.PENDIENTE).count()
        enviados = Recordatorio.objects.filter(estado=EstadoRecordatorio.ENVIADO).count()
        fallidos = Recordatorio.objects.filter(estado=EstadoRecordatorio.FALLIDO).count()
        
        self.stdout.write('\n📊 ESTADÍSTICAS GENERALES')
        self.stdout.write(f"📧 Total recordatorios: {total_recordatorios}")
        self.stdout.write(f"⏳ Pendientes: {pendientes}")
        self.stdout.write(f"✅ Enviados: {enviados}")
        self.stdout.write(f"❌ Fallidos: {fallidos}")
        
        if total_recordatorios > 0:
            tasa_pendientes = (pendientes / total_recordatorios) * 100
            self.stdout.write(f"📊 Pendientes: {tasa_pendientes:.1f}%")
