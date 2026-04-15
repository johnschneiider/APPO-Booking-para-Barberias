// Archivo de debug para el calendario
console.log('=== DEBUG CALENDARIO - ARCHIVO CARGADO ===');

// Función para diagnosticar el problema de las reservas
window.diagnosticarReservas = async function() {
    console.log('=== DIAGNÓSTICO COMPLETO DE RESERVAS ===');
    
    // 1. Verificar el estado del calendario
    console.log('1. VERIFICANDO ESTADO DEL CALENDARIO');
    const calendarGrid = document.getElementById('calendarGrid');
    if (calendarGrid) {
        console.log('✅ Grid del calendario encontrado');
        console.log('  - ID:', calendarGrid.id);
        console.log('  - Clases:', calendarGrid.className);
        console.log('  - Contenido HTML:', calendarGrid.innerHTML.substring(0, 200) + '...');
    } else {
        console.log('❌ Grid del calendario NO encontrado');
        return;
    }
    
    // 2. Verificar celdas del calendario
    console.log('\n2. VERIFICANDO CELDAS DEL CALENDARIO');
    const celdas = document.querySelectorAll('.time-slot[data-profesional]');
    console.log(`  - Total de celdas: ${celdas.length}`);
    
    if (celdas.length > 0) {
        console.log('  - Primera celda:', celdas[0]);
        console.log('  - Atributos de la primera celda:', {
            profesional: celdas[0].getAttribute('data-profesional'),
            hora: celdas[0].getAttribute('data-hora'),
            fecha: celdas[0].getAttribute('data-fecha')
        });
        
        // Mostrar algunas celdas más
        for (let i = 1; i < Math.min(5, celdas.length); i++) {
            const celda = celdas[i];
            console.log(`  - Celda ${i}:`, {
                profesional: celda.getAttribute('data-profesional'),
                hora: celda.getAttribute('data-hora'),
                fecha: celda.getAttribute('data-fecha')
            });
        }
    } else {
        console.log('❌ No hay celdas con data-profesional');
    }
    
    // 3. Verificar profesionales cargados
    console.log('\n3. VERIFICANDO PROFESIONALES');
    if (typeof profesionales !== 'undefined') {
        console.log(`  - Total de profesionales: ${profesionales.length}`);
        console.log('  - Profesionales:', profesionales);
    } else {
        console.log('❌ Variable profesionales no definida');
    }
    
    // 4. Verificar fecha seleccionada
    console.log('\n4. VERIFICANDO FECHA SELECCIONADA');
    if (typeof fechaSeleccionada !== 'undefined') {
        console.log(`  - Fecha seleccionada: ${fechaSeleccionada}`);
    } else {
        console.log('❌ Variable fechaSeleccionada no definida');
    }
    
    // 5. Probar la API directamente
    console.log('\n5. PROBANDO API DIRECTAMENTE');
    try {
        const negocioId = '133'; // ID del negocio
        const fecha = fechaSeleccionada || new Date().toISOString().split('T')[0];
        const url = `/negocios/${negocioId}/api/reservas-dia/?fecha=${fecha}`;
        
        console.log(`  - URL a probar: ${url}`);
        console.log(`  - Fecha a probar: ${fecha}`);
        
        const response = await fetch(url);
        console.log(`  - Respuesta de la API: ${response.status} ${response.statusText}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`  - Datos recibidos:`, data);
            console.log(`  - Número de reservas: ${data.reservas ? data.reservas.length : 0}`);
            
            if (data.reservas && data.reservas.length > 0) {
                console.log('  - Primera reserva:', data.reservas[0]);
                
                // 6. Simular la búsqueda de celda
                console.log('\n6. SIMULANDO BÚSQUEDA DE CELDA');
                const reserva = data.reservas[0];
                const profesionalId = reserva.profesional_id;
                const horaInicio = reserva.hora_inicio;
                const hora = horaInicio.split(':')[0];
                
                console.log(`  - Profesional ID de la API: ${profesionalId}`);
                console.log(`  - Hora extraída: ${hora}`);
                
                // Convertir ID del profesional
                let profesionalIdCalendario = profesionalId;
                if (profesionalId.startsWith('prof_')) {
                    profesionalIdCalendario = profesionalId.replace('prof_', '');
                }
                console.log(`  - Profesional ID para calendario: ${profesionalIdCalendario}`);
                
                // Buscar la celda
                const selector = `[data-profesional="${profesionalIdCalendario}"][data-hora="${hora}"]`;
                console.log(`  - Selector usado: ${selector}`);
                
                const celda = document.querySelector(selector);
                if (celda) {
                    console.log('✅ Celda encontrada para la reserva');
                    console.log('  - Celda:', celda);
                    console.log('  - Atributos:', {
                        profesional: celda.getAttribute('data-profesional'),
                        hora: celda.getAttribute('data-hora'),
                        fecha: celda.getAttribute('data-fecha')
                    });
                    
                    // 7. Crear y agregar la reserva
                    console.log('\n7. CREANDO Y AGREGANDO RESERVA');
                    const reservaElement = document.createElement('div');
                    reservaElement.className = 'reserva-item';
                    reservaElement.setAttribute('data-estado', reserva.estado || 'confirmada');
                    reservaElement.innerHTML = `
                        <div class="reserva-cliente">${reserva.cliente || 'Cliente'}</div>
                        <div class="reserva-servicio">${reserva.servicio || 'Servicio'}</div>
                        <div class="reserva-hora">${horaInicio} - ${reserva.hora_fin}</div>
                    `;
                    
                    console.log('  - Elemento de reserva creado:', reservaElement);
                    console.log('  - HTML del elemento:', reservaElement.outerHTML);
                    
                    celda.appendChild(reservaElement);
                    console.log('✅ Reserva agregada al calendario');
                    
                    // Verificar que se agregó
                    setTimeout(() => {
                        const reservasEnDOM = document.querySelectorAll('.reserva-item');
                        console.log(`  - Reservas en DOM después de agregar: ${reservasEnDOM.length}`);
                        if (reservasEnDOM.length > 0) {
                            console.log('  - Última reserva agregada:', reservasEnDOM[reservasEnDOM.length - 1]);
                        }
                    }, 100);
                    
                } else {
                    console.log('❌ No se encontró celda para la reserva');
                    console.log('  - Celdas disponibles con data-profesional:');
                    document.querySelectorAll('.time-slot[data-profesional]').forEach((celda, idx) => {
                        console.log(`    Celda ${idx}:`, {
                            profesional: celda.getAttribute('data-profesional'),
                            hora: celda.getAttribute('data-hora')
                        });
                    });
                }
            } else {
                console.log('  - No hay reservas para mostrar');
            }
        } else {
            console.log('❌ Error en la API:', response.statusText);
        }
    } catch (error) {
        console.log('❌ Error probando API:', error);
    }
    
    console.log('\n=== DIAGNÓSTICO COMPLETADO ===');
};

// Función para limpiar y recargar todo
window.recargarCalendarioCompleto = async function() {
    console.log('=== RECARGANDO CALENDARIO COMPLETO ===');
    
    // 1. Limpiar reservas existentes
    const reservasExistentes = document.querySelectorAll('.reserva-item');
    console.log(`Limpiando ${reservasExistentes.length} reservas existentes`);
    reservasExistentes.forEach(el => el.remove());
    
    // 2. Regenerar calendario
    if (typeof generarCalendario === 'function') {
        console.log('Regenerando calendario...');
        generarCalendario();
        
        // 3. Cargar reservas después de un delay
        setTimeout(async () => {
            if (typeof cargarReservasDia === 'function') {
                console.log('Cargando reservas del día...');
                await cargarReservasDia();
            } else {
                console.log('❌ Función cargarReservasDia no disponible');
            }
        }, 500);
    } else {
        console.log('❌ Función generarCalendario no disponible');
    }
    
    console.log('=== RECARGA COMPLETADA ===');
};

console.log('Funciones de debug disponibles:');
console.log('  - diagnosticarReservas()');
console.log('  - recargarCalendarioCompleto()');
console.log('=== DEBUG CALENDARIO - ARCHIVO CARGADO ===');
