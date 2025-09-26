#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from negocios.models import Negocio
from suscripciones.models import PlanSuscripcion
from django.db import connection

def diagnosticar_problemas():
    print("=== DIAGNÓSTICO COMPLETO DE PROBLEMAS ===\n")
    
    # 1. Verificar todos los negocios
    print("🔍 1. VERIFICANDO TODOS LOS NEGOCIOS:")
    todos_negocios = Negocio.objects.all()
    print(f"   Total negocios en BD: {todos_negocios.count()}")
    
    for negocio in todos_negocios:
        estado = "✅ ACTIVO" if negocio.activo else "❌ INACTIVO"
        print(f"   - {negocio.nombre} (ID: {negocio.id}): {estado}")
    
    print("\n" + "=" * 60)
    
    # 2. Verificar negocios activos vs inactivos
    print("🔍 2. VERIFICANDO NEGOCIOS ACTIVOS/INACTIVOS:")
    negocios_activos = Negocio.objects.filter(activo=True)
    negocios_inactivos = Negocio.objects.filter(activo=False)
    
    print(f"   Negocios activos: {negocios_activos.count()}")
    print(f"   Negocios inactivos: {negocios_inactivos.count()}")
    
    if negocios_inactivos.exists():
        print("   Negocios inactivos:")
        for negocio in negocios_inactivos:
            print(f"      - {negocio.nombre} (ID: {negocio.id})")
    
    print("\n" + "=" * 60)
    
    # 3. Verificar planes de suscripción
    print("🔍 3. VERIFICANDO PLANES DE SUSCRIPCIÓN:")
    todos_planes = PlanSuscripcion.objects.all()
    planes_activos = PlanSuscripcion.objects.filter(activo=True)
    planes_inactivos = PlanSuscripcion.objects.filter(activo=False)
    
    print(f"   Total planes: {todos_planes.count()}")
    print(f"   Planes activos: {planes_activos.count()}")
    print(f"   Planes inactivos: {planes_inactivos.count()}")
    
    if planes_activos.exists():
        print("   Planes activos:")
        for plan in planes_activos:
            estado_negocio = "✅ ACTIVO" if plan.negocio.activo else "❌ INACTIVO"
            print(f"      - {plan.nombre} (ID: {plan.id}): ${plan.precio_mensual} - Negocio: {plan.negocio.nombre} ({estado_negocio})")
    
    print("\n" + "=" * 60)
    
    # 4. Simular la consulta de negocio_publico
    print("🔍 4. SIMULANDO CONSULTA DE negocio_publico:")
    for negocio in negocios_activos[:3]:  # Solo los primeros 3 para no saturar
        print(f"\n   Negocio: {negocio.nombre} (ID: {negocio.id})")
        
        # Consulta exacta de negocio_publico
        planes_suscripcion = PlanSuscripcion.objects.filter(
            negocio=negocio,
            activo=True
        ).order_by('precio_mensual')
        
        print(f"      Planes encontrados: {planes_suscripcion.count()}")
        if planes_suscripcion.exists():
            for plan in planes_suscripcion:
                print(f"         - {plan.nombre}: ${plan.precio_mensual}")
        else:
            print("         ❌ No se encontraron planes")
    
    print("\n" + "=" * 60)
    
    # 5. Verificar si hay problemas de SQL
    print("🔍 5. VERIFICANDO CONSULTAS SQL:")
    try:
        # Consulta directa SQL
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT n.id, n.nombre, n.activo, COUNT(p.id) as planes_activos
                FROM negocios_negocio n
                LEFT JOIN suscripciones_plansuscripcion p ON n.id = p.negocio_id AND p.activo = 1
                GROUP BY n.id, n.nombre, n.activo
                ORDER BY n.id
            """)
            
            resultados = cursor.fetchall()
            print("   Consulta SQL directa:")
            for row in resultados:
                negocio_id, nombre, activo, planes = row
                estado = "✅ ACTIVO" if activo else "❌ INACTIVO"
                print(f"      - {nombre} (ID: {negocio_id}): {estado} - Planes: {planes}")
                
    except Exception as e:
        print(f"   ❌ Error en consulta SQL: {e}")
    
    print("\n" + "=" * 60)
    
    # 6. Verificar si hay algún problema con el modelo PlanSuscripcion
    print("🔍 6. VERIFICANDO MODELO PLAN SUSCRIPCIÓN:")
    try:
        # Verificar que se puede hacer la consulta básica
        test_query = PlanSuscripcion.objects.all()
        print(f"   ✅ Consulta básica funciona: {test_query.count()} planes")
        
        # Verificar que se puede filtrar por negocio
        test_negocio = Negocio.objects.first()
        if test_negocio:
            planes_negocio = PlanSuscripcion.objects.filter(negocio=test_negocio)
            print(f"   ✅ Filtro por negocio funciona: {planes_negocio.count()} planes para {test_negocio.nombre}")
        
        # Verificar que se puede filtrar por activo
        planes_activos_test = PlanSuscripcion.objects.filter(activo=True)
        print(f"   ✅ Filtro por activo funciona: {planes_activos_test.count()} planes activos")
        
    except Exception as e:
        print(f"   ❌ Error con el modelo: {e}")

if __name__ == "__main__":
    diagnosticar_problemas()
