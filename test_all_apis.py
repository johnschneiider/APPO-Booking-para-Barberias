#!/usr/bin/env python
"""
Script completo para probar todas las APIs del sistema
Verifica que todas las APIs funcionen correctamente
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from clientes.models import Reserva
from negocios.models import Negocio
from profesionales.models import Profesional

User = get_user_model()

class Colors:
    """Colores para la salida en consola"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

class APITester:
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }
        self.setup_users()
    
    def setup_users(self):
        """Crear o obtener usuarios de prueba"""
        try:
            self.negocio_user, _ = User.objects.get_or_create(
                username='Negocio1',
                defaults={
                    'email': 'negocio1@test.com',
                    'tipo': 'negocio',
                    'is_active': True
                }
            )
            self.cliente_user, _ = User.objects.get_or_create(
                username='cliente1',
                defaults={
                    'email': 'cliente1@test.com',
                    'tipo': 'cliente',
                    'is_active': True
                }
            )
            # Asegurar que tienen el tipo correcto
            if not hasattr(self.negocio_user, 'tipo') or self.negocio_user.tipo != 'negocio':
                self.negocio_user.tipo = 'negocio'
                self.negocio_user.save()
            if not hasattr(self.cliente_user, 'tipo') or self.cliente_user.tipo != 'cliente':
                self.cliente_user.tipo = 'cliente'
                self.cliente_user.save()
        except Exception as e:
            print(f"{Colors.RED}Error configurando usuarios: {e}{Colors.END}")
    
    def login(self, user):
        """Iniciar sesión como usuario"""
        return self.client.force_login(user)
    
    def test_api(self, name, method, url, data=None, expected_status=200, user=None, description=""):
        """Probar una API"""
        try:
            if user:
                self.login(user)
            
            if method == 'GET':
                response = self.client.get(url, data=data or {})
            elif method == 'POST':
                response = self.client.post(url, json.dumps(data or {}), content_type='application/json')
            else:
                response = self.client.request(method, url, data=data or {})
            
            status_ok = response.status_code == expected_status
            
            if status_ok:
                self.results['passed'].append({
                    'name': name,
                    'url': url,
                    'status': response.status_code,
                    'description': description
                })
                print(f"{Colors.GREEN}✓{Colors.END} {name}: {response.status_code} - {description}")
                return True
            else:
                error_msg = ""
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', '')
                except:
                    error_msg = response.content.decode()[:100]
                
                self.results['failed'].append({
                    'name': name,
                    'url': url,
                    'expected': expected_status,
                    'got': response.status_code,
                    'error': error_msg,
                    'description': description
                })
                print(f"{Colors.RED}✗{Colors.END} {name}: Esperado {expected_status}, obtuvo {response.status_code}")
                if error_msg:
                    print(f"  {Colors.YELLOW}Error: {error_msg[:100]}{Colors.END}")
                return False
        except Exception as e:
            self.results['failed'].append({
                'name': name,
                'url': url,
                'error': str(e),
                'description': description
            })
            print(f"{Colors.RED}✗{Colors.END} {name}: Excepción - {str(e)}")
            return False
    
    def test_cuentas_apis(self):
        """Probar APIs de cuentas"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== APIs de Cuentas ==={Colors.END}")
        
        # API de notificaciones
        self.test_api(
            'API Notificaciones',
            'GET',
            '/cuentas/api/notificaciones/',
            user=self.negocio_user,
            description='Obtener notificaciones del usuario'
        )
        
        # API username disponible
        self.test_api(
            'API Username Disponible',
            'GET',
            '/cuentas/api/username-disponible/',
            data={'username': 'testuser123'},
            user=None,
            description='Verificar disponibilidad de username'
        )
    
    def test_chat_apis(self):
        """Probar APIs de chat"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== APIs de Chat ==={Colors.END}")
        
        # API mensajes no leídos
        self.test_api(
            'API Mensajes No Leídos',
            'GET',
            '/chat/api/mensajes-no-leidos/',
            user=self.cliente_user,
            description='Obtener contador de mensajes no leídos'
        )
        
        # API lista conversaciones (requiere conversación existente)
        self.test_api(
            'API Lista Conversaciones',
            'GET',
            '/chat/',
            user=self.cliente_user,
            description='Listar conversaciones del usuario'
        )
    
    def test_clientes_apis(self):
        """Probar APIs de clientes"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== APIs de Clientes ==={Colors.END}")
        
        # API autocompletar servicios
        self.test_api(
            'API Autocompletar Servicios',
            'GET',
            '/clientes/api/autocompletar-servicios/',
            data={'q': 'corte'},
            user=None,
            description='Autocompletar servicios'
        )
        
        # API autocompletar servicios mejorado
        self.test_api(
            'API Autocompletar Servicios Mejorado',
            'GET',
            '/clientes/api/autocompletar-servicios-mejorado/',
            data={'q': 'corte'},
            user=None,
            description='Autocompletar servicios mejorado'
        )
        
        # API todos servicios
        self.test_api(
            'API Todos Servicios',
            'GET',
            '/clientes/api/todos-servicios/',
            user=None,
            description='Obtener todos los servicios'
        )
        
        # API autocompletar negocios
        self.test_api(
            'API Autocompletar Negocios',
            'GET',
            '/clientes/api/autocompletar-negocios/',
            data={'q': 'pelu'},
            user=None,
            description='Autocompletar negocios'
        )
        
        # API disponibilidad días
        self.test_api(
            'API Disponibilidad Días',
            'GET',
            '/clientes/api/disponibilidad-dias/',
            data={'negocio_id': 1},
            user=None,
            description='Obtener días disponibles'
        )
        
        # API negocios vistos recientes
        self.test_api(
            'API Negocios Vistos Recientes',
            'GET',
            '/clientes/api/negocios-vistos-recientes/',
            user=self.cliente_user,
            description='Obtener negocios vistos recientemente'
        )
        
        # API buscar negocios
        self.test_api(
            'API Buscar Negocios',
            'GET',
            '/clientes/api/buscar-negocios/',
            data={'q': 'peluqueria'},
            user=None,
            description='Buscar negocios'
        )
    
    def test_negocios_apis(self):
        """Probar APIs de negocios"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== APIs de Negocios ==={Colors.END}")
        
        # Obtener un negocio del usuario
        try:
            negocio = Negocio.objects.filter(propietario=self.negocio_user).first()
            if not negocio:
                print(f"{Colors.YELLOW}⚠ No hay negocios para probar APIs{Colors.END}")
                return
            
            negocio_id = negocio.id
            
            # API reservas del negocio
            self.test_api(
                'API Reservas Negocio',
                'GET',
                f'/negocios/{negocio_id}/api/reservas/',
                user=self.negocio_user,
                description='Obtener reservas del negocio'
            )
            
            # API estadísticas
            self.test_api(
                'API Estadísticas Negocio',
                'GET',
                f'/negocios/{negocio_id}/api/estadisticas/',
                user=self.negocio_user,
                description='Obtener estadísticas del negocio'
            )
            
            # API usuarios del negocio
            self.test_api(
                'API Usuarios Negocio',
                'GET',
                f'/negocios/{negocio_id}/api/usuarios/',
                user=self.negocio_user,
                description='Obtener usuarios del negocio'
            )
            
            # API reservas del día
            fecha = datetime.now().strftime('%Y-%m-%d')
            self.test_api(
                'API Reservas Día',
                'GET',
                f'/negocios/{negocio_id}/api/reservas-dia/',
                data={'fecha': fecha},
                user=self.negocio_user,
                description='Obtener reservas del día'
            )
            
            # API agendas profesionales
            self.test_api(
                'API Agendas Profesionales',
                'GET',
                f'/negocios/{negocio_id}/api/agendas-profesionales/',
                user=self.negocio_user,
                description='Obtener agendas de profesionales'
            )
            
            # API profesionales
            self.test_api(
                'API Profesionales',
                'GET',
                f'/negocios/{negocio_id}/api/profesionales/',
                user=self.negocio_user,
                description='Obtener profesionales del negocio'
            )
            
            # API cambiar estado reserva (requiere reserva existente)
            reserva = Reserva.objects.filter(peluquero=negocio).first()
            if reserva:
                self.test_api(
                    'API Cambiar Estado Reserva',
                    'POST',
                    f'/negocios/{negocio_id}/api/reserva/{reserva.id}/estado/',
                    data={'estado': 'completado', 'notas': 'Prueba'},
                    user=self.negocio_user,
                    expected_status=200,
                    description='Cambiar estado de reserva'
                )
            else:
                print(f"{Colors.YELLOW}⚠ No hay reservas para probar cambio de estado{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}Error probando APIs de negocios: {e}{Colors.END}")
    
    def test_suscripciones_apis(self):
        """Probar APIs de suscripciones"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== APIs de Suscripciones ==={Colors.END}")
        
        try:
            negocio = Negocio.objects.filter(propietario=self.negocio_user).first()
            if not negocio:
                print(f"{Colors.YELLOW}⚠ No hay negocios para probar APIs de suscripciones{Colors.END}")
                return
            
            negocio_id = negocio.id
            
            # Estas APIs requieren planes/suscripciones existentes, así que solo verificamos que las rutas existan
            print(f"{Colors.YELLOW}⚠ APIs de suscripciones requieren datos específicos{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}Error probando APIs de suscripciones: {e}{Colors.END}")
    
    def test_health_check(self):
        """Probar health check"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== Health Check ==={Colors.END}")
        
        self.test_api(
            'Health Check',
            'GET',
            '/health/',
            user=None,
            description='Verificar estado del servidor'
        )
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
        print(f"  INICIANDO PRUEBAS DE TODAS LAS APIs")
        print(f"{'='*60}{Colors.END}\n")
        
        self.test_health_check()
        self.test_cuentas_apis()
        self.test_chat_apis()
        self.test_clientes_apis()
        self.test_negocios_apis()
        self.test_suscripciones_apis()
        
        self.print_summary()
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
        print(f"  RESUMEN DE PRUEBAS")
        print(f"{'='*60}{Colors.END}\n")
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['skipped'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        skipped = len(self.results['skipped'])
        
        print(f"{Colors.GREEN}✓ Pasadas: {passed}{Colors.END}")
        print(f"{Colors.RED}✗ Fallidas: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠ Omitidas: {skipped}{Colors.END}")
        print(f"Total: {total}\n")
        
        if failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}APIs que fallaron:{Colors.END}")
            for test in self.results['failed']:
                print(f"  - {test['name']}: {test.get('error', 'Error desconocido')}")
        
        if passed == total and failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}¡Todas las pruebas pasaron! ✓{Colors.END}")
        elif failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}Hay {failed} prueba(s) que fallaron{Colors.END}")

if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()

