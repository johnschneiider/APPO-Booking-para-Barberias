from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.db import models
import logging

from .models import PlanSuscripcion, Suscripcion, PagoSuscripcion, BeneficioSuscripcion
from negocios.models import Negocio

# Obtener el modelo de usuario personalizado
User = get_user_model()

# Configurar el logger
logger = logging.getLogger(__name__)

# ===== VISTAS PARA NEGOCIOS =====

@login_required
def planes_negocio(request, negocio_id):
    """Vista para que el negocio gestione sus planes de suscripción"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    planes = PlanSuscripcion.objects.filter(negocio=negocio).order_by('-fecha_creacion')
    
    # Calcular estadísticas
    total_planes = planes.count()
    planes_activos = planes.filter(activo=True).count()
    total_suscriptores = Suscripcion.objects.filter(plan__negocio=negocio, estado='activa').count()
    ingresos_mensuales = sum(
        plan.precio_mensual * plan.suscripciones.filter(estado='activa').count()
        for plan in planes.filter(activo=True)
    )
    
    # Los campos total_suscriptores e ingresos_mensuales ya están disponibles como propiedades
    # No necesitamos asignarlos manualmente
    
    context = {
        'negocio': negocio,
        'planes': planes,
        'total_planes': total_planes,
        'planes_activos': planes_activos,
        'total_suscriptores': total_suscriptores,
        'ingresos_mensuales': ingresos_mensuales,
    }
    
    return render(request, 'suscripciones/planes_negocio.html', context)

@login_required
def crear_plan(request, negocio_id):
    """Vista para crear un nuevo plan de suscripción"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            precio_mensual = request.POST.get('precio_mensual')
            duracion_meses = request.POST.get('duracion_meses', 12)
            activo = request.POST.get('activo') == 'true'
            destacado = request.POST.get('destacado') == 'on'
            limite_suscriptores = request.POST.get('limite_suscriptores', 0)
            
            # Validar campos requeridos
            if not nombre or not precio_mensual:
                messages.error(request, 'Nombre y precio son campos requeridos')
                return render(request, 'suscripciones/crear_plan_negocio.html', {'negocio': negocio})
            
            try:
                precio_mensual = Decimal(precio_mensual)
                if precio_mensual <= 0:
                    messages.error(request, 'El precio debe ser mayor a 0')
                    return render(request, 'suscripciones/crear_plan_negocio.html', {'negocio': negocio})
            except (ValueError, TypeError):
                messages.error(request, 'Precio inválido')
                return render(request, 'suscripciones/crear_plan_negocio.html', {'negocio': negocio})
            
            # Crear el plan
            plan = PlanSuscripcion.objects.create(
                negocio=negocio,
                nombre=nombre,
                descripcion=descripcion,
                precio_mensual=precio_mensual,
                duracion_meses=int(duracion_meses),
                activo=activo,
                destacado=destacado,
                limite_suscriptores=int(limite_suscriptores) if limite_suscriptores else 0
            )
            
            # Procesar beneficios si existen
            beneficios = request.POST.getlist('beneficios[]')
            for beneficio_texto in beneficios:
                if beneficio_texto.strip():
                    BeneficioSuscripcion.objects.create(
                        plan=plan,
                        descripcion=beneficio_texto.strip(),
                        activo=True,
                        orden=0
                    )
            
            # Procesar imagen si se subió
            if 'imagen' in request.FILES:
                plan.imagen = request.FILES['imagen']
                plan.save()
            
            messages.success(request, f'Plan "{nombre}" creado exitosamente')
            return redirect('suscripciones:planes_negocio', negocio_id=negocio_id)
            
        except Exception as e:
            logger.error(f"Error creando plan: {e}")
            messages.error(request, 'Error al crear el plan. Por favor, intenta nuevamente.')
    
    context = {
        'negocio': negocio,
    }
    
    return render(request, 'suscripciones/crear_plan_negocio.html', context)

@login_required
def editar_plan(request, negocio_id, plan_id):
    """Vista para editar un plan de suscripción existente"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    plan = get_object_or_404(PlanSuscripcion, id=plan_id, negocio=negocio)
    
    if request.method == 'POST':
        # Aquí se procesaría el formulario
        messages.success(request, 'Plan actualizado exitosamente')
        return redirect('suscripciones:planes_negocio', negocio_id=negocio_id)
    
    context = {
        'negocio': negocio,
        'plan': plan,
    }
    
    return render(request, 'suscripciones/plan_suscripcion_form.html', context)

@login_required
def negocio_suscripciones(request, negocio_id):
    """Vista para que el negocio vea sus suscripciones activas"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    suscripciones = Suscripcion.objects.filter(plan__negocio=negocio).select_related('cliente', 'plan').order_by('-fecha_inicio')
    planes = PlanSuscripcion.objects.filter(negocio=negocio, activo=True)
    
    # Calcular estadísticas
    total_suscripciones = suscripciones.count()
    suscripciones_activas = suscripciones.filter(estado='activa').count()
    proximas_vencer = suscripciones.filter(estado='proxima_vencer').count()
    ingresos_mensuales = sum(
        suscripcion.plan.precio_mensual 
        for suscripcion in suscripciones.filter(estado='activa')
    )
    
    context = {
        'negocio': negocio,
        'suscripciones': suscripciones,
        'planes': planes,
        'total_suscripciones': total_suscripciones,
        'suscripciones_activas': suscripciones_activas,
        'proximas_vencer': proximas_vencer,
        'ingresos_mensuales': ingresos_mensuales,
    }
    
    return render(request, 'suscripciones/negocio_suscripciones.html', context)

@login_required
def dashboard_suscripciones(request, negocio_id):
    """Dashboard de suscripciones para el negocio"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    # Obtener datos para el dashboard
    suscripciones = Suscripcion.objects.filter(plan__negocio=negocio)
    planes = PlanSuscripcion.objects.filter(negocio=negocio)
    
    # Calcular métricas
    total_suscripciones = suscripciones.count()
    suscripciones_activas = suscripciones.filter(estado='activa').count()
    proximas_vencer = suscripciones.filter(estado='proxima_vencer').count()
    ingresos_mensuales = sum(
        suscripcion.plan.precio_mensual 
        for suscripcion in suscripciones.filter(estado='activa')
    )
    
    # Calcular crecimiento (simulado)
    crecimiento_suscripciones = 15
    crecimiento_activas = 8
    crecimiento_ingresos = 12
    
    # Top planes
    top_planes = planes.annotate(
        total_suscriptores=models.Count('suscripcion', filter=models.Q(suscripcion__estado='activa'))
    ).order_by('-total_suscriptores')[:5]
    
    # Suscripciones recientes
    suscripciones_recientes = suscripciones.select_related('cliente', 'plan').order_by('-fecha_inicio')[:10]
    
    context = {
        'negocio': negocio,
        'total_suscripciones': total_suscripciones,
        'suscripciones_activas': suscripciones_activas,
        'proximas_vencer': proximas_vencer,
        'ingresos_mensuales': ingresos_mensuales,
        'crecimiento_suscripciones': crecimiento_suscripciones,
        'crecimiento_activas': crecimiento_activas,
        'crecimiento_ingresos': crecimiento_ingresos,
        'top_planes': top_planes,
        'suscripciones_recientes': suscripciones_recientes,
        'alertas': [],
        'proximas_acciones': [],
        'actividades_recientes': [],
    }
    
    return render(request, 'suscripciones/dashboard_suscripciones.html', context)

# ===== VISTAS PARA CLIENTES =====

@login_required
def cliente_suscripciones(request):
    """Vista para que el cliente vea sus suscripciones"""
    suscripciones = Suscripcion.objects.filter(cliente=request.user).select_related('negocio', 'plan').order_by('-fecha_inicio')
    
    context = {
        'suscripciones': suscripciones,
    }
    
    return render(request, 'suscripciones/cliente_suscripciones.html', context)

def planes_disponibles(request):
    """Vista para mostrar todos los planes disponibles"""
    planes = PlanSuscripcion.objects.filter(activo=True).select_related('negocio').order_by('-fecha_creacion')
    
    # Aplicar paginación si es necesario
    from django.core.paginator import Paginator
    paginator = Paginator(planes, 12)  # 12 planes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'planes': page_obj,
    }
    
    return render(request, 'suscripciones/planes_disponibles.html', context)

# ===== VISTAS DE API =====

@login_required
def api_suscripcion_detalles(request, negocio_id, suscripcion_id):
    """API para obtener detalles de una suscripción"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    try:
        suscripcion = Suscripcion.objects.get(id=suscripcion_id, plan__negocio=negocio)
        
        data = {
            'id': suscripcion.id,
            'cliente': {
                'id': suscripcion.cliente.id,
                'username': suscripcion.cliente.username,
                'email': suscripcion.cliente.email,
                'telefono': getattr(suscripcion.cliente, 'telefono', ''),
            },
            'plan': {
                'id': suscripcion.plan.id,
                'nombre': suscripcion.plan.nombre,
                'precio_mensual': float(suscripcion.plan.precio_mensual),
            },
            'estado': suscripcion.estado,
            'fecha_inicio': suscripcion.fecha_inicio.isoformat(),
            'fecha_fin': suscripcion.fecha_fin.isoformat() if suscripcion.fecha_fin else None,
            'fecha_renovacion': suscripcion.fecha_renovacion.isoformat() if suscripcion.fecha_renovacion else None,
            'activa': suscripcion.estado == 'activa',
        }
        
        return JsonResponse(data)
        
    except Suscripcion.DoesNotExist:
        return JsonResponse({'error': 'Suscripción no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error obteniendo detalles de suscripción {suscripcion_id}: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
def api_renovar_suscripcion(request, negocio_id, suscripcion_id):
    """API para renovar una suscripción"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    try:
        suscripcion = Suscripcion.objects.get(id=suscripcion_id, plan__negocio=negocio)
        
        if suscripcion.estado != 'activa':
            return JsonResponse({'error': 'Solo se pueden renovar suscripciones activas'}, status=400)
        
        # Lógica de renovación aquí
        suscripcion.fecha_renovacion = timezone.now()
        suscripcion.save()
        
        return JsonResponse({'message': 'Suscripción renovada exitosamente'})
        
    except Suscripcion.DoesNotExist:
        return JsonResponse({'error': 'Suscripción no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error renovando suscripción {suscripcion_id}: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
def api_enviar_recordatorio(request, negocio_id, suscripcion_id):
    """API para enviar recordatorio de renovación"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    try:
        suscripcion = Suscripcion.objects.get(id=suscripcion_id, plan__negocio=negocio)
        
        # Lógica de envío de recordatorio aquí
        # Por ahora solo retornamos éxito
        
        return JsonResponse({'message': 'Recordatorio enviado exitosamente'})
        
    except Suscripcion.DoesNotExist:
        return JsonResponse({'error': 'Suscripción no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error enviando recordatorio para suscripción {suscripcion_id}: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
def api_plan_detalles(request, negocio_id, plan_id):
    """API para obtener detalles de un plan"""
    negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
    
    try:
        plan = PlanSuscripcion.objects.get(id=plan_id, negocio=negocio)
        
        # Obtener estadísticas del plan
        total_suscriptores = plan.suscripciones.filter(estado='activa').count()
        ingresos_mensuales = total_suscriptores * plan.precio_mensual
        
        # Obtener beneficios del plan
        beneficios = []
        if hasattr(plan, 'beneficios'):
            beneficios = [
                {
                    'id': beneficio.id,
                    'descripcion': beneficio.descripcion,
                    'activo': beneficio.activo,
                    'orden': beneficio.orden
                }
                for beneficio in plan.beneficios.filter(activo=True).order_by('orden')
            ]
        
        data = {
            'id': plan.id,
            'nombre': plan.nombre,
            'descripcion': plan.descripcion,
            'precio_mensual': float(plan.precio_mensual),
            'activo': plan.activo,
            'destacado': getattr(plan, 'destacado', False),
            'duracion_meses': getattr(plan, 'duracion_meses', 12),
            'limite_suscriptores': getattr(plan, 'limite_suscriptores', 0),
            'negocio_nombre': plan.negocio.nombre,
            'fecha_creacion': plan.fecha_creacion.isoformat(),
            'fecha_actualizacion': plan.fecha_actualizacion.isoformat(),
            'total_suscriptores': total_suscriptores,
            'ingresos_mensuales': float(ingresos_mensuales),
            'beneficios': beneficios
        }
        
        logger.info(f"Detalles del plan {plan_id} enviados exitosamente")
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error obteniendo detalles del plan {plan_id}: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@require_http_methods(["DELETE"])
@login_required
def api_eliminar_plan(request, negocio_id, plan_id):
    """API para eliminar un plan"""
    logger.info(f"=== INICIO api_eliminar_plan ===")
    logger.info(f"Usuario: {request.user.username}")
    logger.info(f"Negocio ID: {negocio_id}")
    logger.info(f"Plan ID: {plan_id}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            logger.warning(f"Usuario no autenticado intentando eliminar plan {plan_id}")
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        
        # Verificar que el usuario sea propietario del negocio
        negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
        
        # Obtener el plan
        try:
            plan = PlanSuscripcion.objects.get(id=plan_id, negocio=negocio)
        except PlanSuscripcion.DoesNotExist:
            logger.warning(f"Plan {plan_id} no encontrado en negocio {negocio_id}")
            return JsonResponse({'error': 'Plan no encontrado'}, status=404)
        
        logger.info(f"Usuario {request.user.username} autorizado para eliminar plan {plan_id}")
        
        # Verificar si hay suscripciones activas
        suscripciones_activas = plan.suscripcion_set.filter(estado='activa')
        if suscripciones_activas.exists():
            count_activas = suscripciones_activas.count()
            logger.warning(f"No se puede eliminar plan {plan_id} - tiene {count_activas} suscripción{"es" if count_activas > 1 else ""} activa{"s" if count_activas > 1 else ""}")
            return JsonResponse({
                'error': f'No se puede eliminar un plan con {count_activas} suscripción{"es" if count_activas > 1 else ""} activa{"s" if count_activas > 1 else ""}'
            }, status=400)
        
        # Eliminar el plan
        nombre_plan = plan.nombre
        plan.delete()
        
        logger.info(f"Plan {plan_id} ({nombre_plan}) eliminado exitosamente por usuario {request.user.username}")
        return JsonResponse({
            'success': True, 
            'message': f'Plan "{nombre_plan}" eliminado exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error inesperado en api_eliminar_plan: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    finally:
        logger.info(f"=== FIN api_eliminar_plan ===")

@csrf_protect
@require_http_methods(["POST"])
@login_required
def api_toggle_plan(request, negocio_id, plan_id):
    """API para activar/desactivar un plan"""
    logger.info(f"=== INICIO api_toggle_plan ===")
    logger.info(f"Usuario: {request.user.username}")
    logger.info(f"Negocio ID: {negocio_id}")
    logger.info(f"Plan ID: {plan_id}")
    logger.info(f"Body: {request.body}")
    
    try:
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            logger.warning(f"Usuario no autenticado intentando modificar plan {plan_id}")
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        
        # Verificar que el usuario sea propietario del negocio
        negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
        
        # Obtener el plan
        try:
            plan = PlanSuscripcion.objects.get(id=plan_id, negocio=negocio)
        except PlanSuscripcion.DoesNotExist:
            logger.warning(f"Plan {plan_id} no encontrado en negocio {negocio_id}")
            return JsonResponse({'error': 'Plan no encontrado'}, status=404)
        
        logger.info(f"Usuario {request.user.username} autorizado para modificar plan {plan_id}")
        
        # Procesar el body de la request
        try:
            data = json.loads(request.body)
            activo = data.get('activo', False)
        except json.JSONDecodeError:
            logger.warning(f"Body JSON inválido en request: {request.body}")
            return JsonResponse({'error': 'Formato de datos inválido'}, status=400)
        
        # Actualizar el estado del plan
        estado_anterior = plan.activo
        plan.activo = activo
        plan.save()
        
        logger.info(f"Plan {plan_id} estado cambiado de {estado_anterior} a {activo} por usuario {request.user.username}")
        return JsonResponse({
            'success': True, 
            'message': f'Plan {"activado" if activo else "desactivado"} exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error inesperado en api_toggle_plan: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    finally:
        logger.info(f"=== FIN api_toggle_plan ===")

# ===== VISTAS DE SUSCRIPCIÓN =====

@login_required
def suscribirse_plan(request, plan_id):
    """Vista para suscribirse a un plan"""
    try:
        plan = get_object_or_404(PlanSuscripcion, id=plan_id, activo=True)
        
        # Verificar que el usuario sea cliente
        if not hasattr(request.user, 'tipo') or request.user.tipo != 'cliente':
            messages.error(request, 'Solo los clientes pueden suscribirse a planes')
            return redirect('inicio')
        
        # Verificar si ya tiene una suscripción activa
        suscripcion_existente = Suscripcion.objects.filter(
            cliente=request.user, 
            negocio=plan.negocio, 
            estado='activa'
        ).first()
        
        if suscripcion_existente:
            messages.warning(request, f'Ya tienes una suscripción activa con {plan.negocio.nombre}')
            return redirect('suscripciones:cliente_suscripciones')
        
        if request.method == 'POST':
            try:
                # Crear nueva suscripción
                suscripcion = Suscripcion.objects.create(
                    cliente=request.user,
                    negocio=plan.negocio,
                    plan=plan,
                    fecha_inicio=timezone.now(),
                    fecha_fin=timezone.now() + timedelta(days=30),
                    estado='activa',
                    precio_actual=plan.precio_mensual,
                    moneda='COP'
                )
                
                # Aquí se procesaría el pago real
                # Por ahora solo simulamos la creación
                
                messages.success(request, f'¡Te has suscrito exitosamente al plan {plan.nombre}!')
                logger.info(f"Usuario {request.user.username} se suscribió al plan {plan.id} del negocio {plan.negocio.id}")
                
                return redirect('suscripciones:cliente_suscripciones')
                
            except Exception as e:
                logger.error(f"Error creando suscripción: {e}")
                messages.error(request, 'Hubo un error al procesar tu suscripción. Por favor, inténtalo nuevamente.')
        
        # Obtener información adicional para el contexto
        beneficios = plan.beneficios.all()
        
        context = {
            'plan': plan,
            'beneficios': beneficios,
            'negocio': plan.negocio,
            'suscripcion_existente': suscripcion_existente,
        }
        
        return render(request, 'suscripciones/suscribirse_plan.html', context)
        
    except Exception as e:
        logger.error(f"Error en suscribirse_plan: {e}")
        messages.error(request, 'Error al cargar el plan de suscripción.')
        return redirect('inicio')

@login_required
def cancelar_suscripcion(request, suscripcion_id):
    """Vista para cancelar una suscripción"""
    suscripcion = get_object_or_404(Suscripcion, id=suscripcion_id, cliente=request.user)
    
    if request.method == 'POST':
        suscripcion.estado = 'cancelada'
        suscripcion.fecha_cancelacion = timezone.now().date()
        suscripcion.save()
        
        messages.success(request, 'Suscripción cancelada exitosamente')
        return redirect('suscripciones:cliente_suscripciones')
    
    context = {
        'suscripcion': suscripcion,
    }
    
    return render(request, 'suscripciones/cancelar_suscripcion.html', context)

# ===== NUEVAS VISTAS DE API PARA EDICIÓN DE PLANES =====

@csrf_protect
@login_required
def api_editar_plan(request, negocio_id, plan_id):
    """API para editar un plan de suscripción"""
    logger.info(f"=== INICIO api_editar_plan ===")
    logger.info(f"Usuario: {request.user.username}")
    logger.info(f"Negocio ID: {negocio_id}")
    logger.info(f"Plan ID: {plan_id}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            logger.warning(f"Usuario no autenticado intentando editar plan {plan_id}")
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        
        # Verificar que el usuario sea propietario del negocio
        negocio = get_object_or_404(Negocio, id=negocio_id, propietario=request.user)
        logger.info(f"Usuario {request.user.username} - Negocio encontrado: {negocio}")
        
        logger.info(f"Usuario {request.user.username} intentando editar plan {plan_id} del negocio {negocio.id}")
        
        # Obtener el plan y verificar que pertenezca al negocio
        try:
            plan = PlanSuscripcion.objects.get(id=plan_id, negocio=negocio)
            logger.info(f"Plan {plan_id} encontrado, pertenece al negocio {plan.negocio.id}")
        except PlanSuscripcion.DoesNotExist:
            logger.warning(f"Plan {plan_id} no encontrado en negocio {negocio_id}")
            return JsonResponse({'error': 'Plan no encontrado'}, status=404)
        
        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            precio_mensual = request.POST.get('precio_mensual')
            activo = request.POST.get('activo') == 'true'
            destacado = request.POST.get('destacado') == 'on'
            
            logger.info(f"Datos recibidos: nombre={nombre}, precio={precio_mensual}, activo={activo}, destacado={destacado}")
            
            # Validar campos requeridos
            if not nombre or not precio_mensual:
                return JsonResponse({'error': 'Nombre y precio son campos requeridos'}, status=400)
            
            try:
                precio_mensual = Decimal(precio_mensual)
                if precio_mensual <= 0:
                    return JsonResponse({'error': 'El precio debe ser mayor a 0'}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Precio inválido'}, status=400)
            
            # Actualizar el plan
            plan.nombre = nombre
            plan.descripcion = descripcion
            plan.precio_mensual = precio_mensual
            plan.activo = activo
            
            # Actualizar campo destacado si existe en el modelo
            if hasattr(plan, 'destacado'):
                plan.destacado = destacado
            
            plan.save()
            
            logger.info(f"Plan {plan.id} editado exitosamente por usuario {request.user.username}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Plan actualizado exitosamente',
                'plan': {
                    'id': plan.id,
                    'nombre': plan.nombre,
                    'descripcion': plan.descripcion,
                    'precio_mensual': float(plan.precio_mensual),
                    'activo': plan.activo,
                    'destacado': getattr(plan, 'destacado', False),
                    'fecha_actualizacion': plan.fecha_actualizacion.isoformat()
                }
            })
        
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        
    except Exception as e:
        logger.error(f"Error editando plan {plan_id}: {e}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    finally:
        logger.info(f"=== FIN api_editar_plan ===")
