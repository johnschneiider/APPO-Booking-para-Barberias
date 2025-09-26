// ===== FUNCIONES PRINCIPALES DE SUSCRIPCIONES =====

// Función para filtrar suscripciones
function filtrarSuscripciones() {
    const estadoFilter = document.getElementById('estado-filter').value;
    const planFilter = document.getElementById('plan-filter').value;
    const searchFilter = document.getElementById('search-filter').value.toLowerCase();
    
    const rows = document.querySelectorAll('.suscripcion-row');
    
    rows.forEach(row => {
        const estado = row.dataset.estado;
        const plan = row.dataset.plan;
        const clienteNombre = row.querySelector('.cliente-details h4').textContent.toLowerCase();
        const clienteEmail = row.querySelector('.cliente-details p').textContent.toLowerCase();
        
        let showRow = true;
        
        // Filtro por estado
        if (estadoFilter && estado !== estadoFilter) {
            showRow = false;
        }
        
        // Filtro por plan
        if (planFilter && plan !== planFilter) {
            showRow = false;
        }
        
        // Filtro por búsqueda
        if (searchFilter && !clienteNombre.includes(searchFilter) && !clienteEmail.includes(searchFilter)) {
            showRow = false;
        }
        
        row.style.display = showRow ? '' : 'none';
    });
}

// Función para filtrar planes
function filtrarPlanes() {
    const estadoFilter = document.getElementById('estado-filter').value;
    const destacadoFilter = document.getElementById('destacado-filter').value;
    const searchFilter = document.getElementById('search-filter').value.toLowerCase();
    
    const cards = document.querySelectorAll('.plan-card');
    
    cards.forEach(card => {
        const estado = card.dataset.estado;
        const destacado = card.dataset.destacado;
        const planNombre = card.querySelector('.plan-nombre').textContent.toLowerCase();
        
        let showCard = true;
        
        // Filtro por estado
        if (estadoFilter && estado !== estadoFilter) {
            showCard = false;
        }
        
        // Filtro por destacado
        if (destacadoFilter && destacado !== destacadoFilter) {
            showCard = false;
        }
        
        // Filtro por búsqueda
        if (searchFilter && !planNombre.includes(searchFilter)) {
            showCard = false;
        }
        
        card.style.display = showCard ? '' : 'none';
    });
}

// Función para ver detalles de suscripción
function verDetalles(suscripcionId) {
    // Aquí se cargarían los detalles desde el servidor
    fetch(`/suscripciones/api/suscripcion/${suscripcionId}/detalles/`)
        .then(response => response.json())
        .then(data => {
            const modalBody = document.getElementById('detallesModalBody');
            modalBody.innerHTML = generarHTMLDetalles(data);
            
            const modal = new bootstrap.Modal(document.getElementById('detallesModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error al cargar detalles:', error);
            alert('Error al cargar los detalles de la suscripción');
        });
}

// Función para renovar suscripción
function renovarSuscripcion(suscripcionId) {
    if (confirm('¿Estás seguro de que quieres renovar esta suscripción?')) {
        fetch(`/suscripciones/api/suscripcion/${suscripcionId}/renovar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Suscripción renovada exitosamente');
                location.reload();
            } else {
                alert('Error al renovar la suscripción: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error al renovar:', error);
            alert('Error al renovar la suscripción');
        });
    }
}

// Función para enviar recordatorio
function enviarRecordatorio(suscripcionId) {
    if (confirm('¿Enviar recordatorio de renovación al cliente?')) {
        fetch(`/suscripciones/api/suscripcion/${suscripcionId}/recordatorio/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Recordatorio enviado exitosamente');
            } else {
                alert('Error al enviar recordatorio: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error al enviar recordatorio:', error);
            alert('Error al enviar recordatorio');
        });
    }
}

// Función para ver detalles del plan
function verDetallesPlan(planId) {
    fetch(`/suscripciones/api/plan/${planId}/detalles/`)
        .then(response => response.json())
        .then(data => {
            const modalBody = document.getElementById('detallesPlanModalBody');
            modalBody.innerHTML = generarHTMLDetallesPlan(data);
            
            const modal = new bootstrap.Modal(document.getElementById('detallesPlanModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error al cargar detalles del plan:', error);
            alert('Error al cargar los detalles del plan');
        });
}

// Función para eliminar plan
function eliminarPlan(planId) {
    const modal = new bootstrap.Modal(document.getElementById('eliminarPlanModal'));
    modal.show();
    
    // Guardar el ID del plan a eliminar
    window.planAEliminar = planId;
}

// Función para confirmar eliminación
function confirmarEliminacion() {
    const planId = window.planAEliminar;
    
    fetch(`/suscripciones/api/plan/${planId}/eliminar/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Plan eliminado exitosamente');
            location.reload();
        } else {
            alert('Error al eliminar el plan: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error al eliminar:', error);
        alert('Error al eliminar el plan');
    });
}

// Función para toggle del plan
function togglePlan(planId, activo) {
    fetch(`/suscripciones/api/plan/${planId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ activo: activo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar la UI sin recargar la página
            const card = document.querySelector(`[data-plan-id="${planId}"]`);
            if (card) {
                const statusBadge = card.querySelector('.status-badge');
                if (activo) {
                    statusBadge.className = 'status-badge status-activo';
                    statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Activo';
                } else {
                    statusBadge.className = 'status-badge status-inactivo';
                    statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Inactivo';
                }
            }
        } else {
            alert('Error al cambiar el estado del plan: ' + data.error);
            // Revertir el toggle
            const checkbox = document.getElementById(`toggle-${planId}`);
            checkbox.checked = !activo;
        }
    })
    .catch(error => {
        console.error('Error al cambiar estado:', error);
        alert('Error al cambiar el estado del plan');
        // Revertir el toggle
        const checkbox = document.getElementById(`toggle-${planId}`);
        checkbox.checked = !activo;
    });
}

// Función para mostrar estadísticas
function mostrarEstadisticas() {
    const modal = new bootstrap.Modal(document.getElementById('estadisticasModal'));
    modal.show();
    
    // Aquí se cargarían las estadísticas desde el servidor
    cargarEstadisticas();
}

// Función para exportar datos
function exportarDatos() {
    // Implementar exportación a CSV/Excel
    alert('Función de exportación en desarrollo');
}

// Función para buscar negocios (clientes)
function buscarNegocios() {
    const modal = new bootstrap.Modal(document.getElementById('buscarNegociosModal'));
    modal.show();
}

// Función para realizar búsqueda de negocios
function realizarBusqueda() {
    const categoria = document.getElementById('categoria-filter').value;
    const ubicacion = document.getElementById('ubicacion-filter').value;
    const precio = document.getElementById('precio-filter').value;
    
    // Aquí se implementaría la búsqueda real
    console.log('Búsqueda:', { categoria, ubicacion, precio });
    
    // Simular resultados
    const resultados = document.getElementById('negociosResultados');
    resultados.innerHTML = '<p>Búsqueda en desarrollo...</p>';
}

// Función para ver historial
function verHistorial() {
    const modal = new bootstrap.Modal(document.getElementById('historialModal'));
    modal.show();
    
    // Cargar historial
    cargarHistorial();
}

// Función para suscribirse a un plan
function suscribirse(planId) {
    const modal = new bootstrap.Modal(document.getElementById('suscripcionModal'));
    modal.show();
    
    // Cargar información del plan para suscripción
    cargarInfoSuscripcion(planId);
}

// Función para ver detalles del plan (planes disponibles)
function verDetallesPlan(planId) {
    fetch(`/suscripciones/api/plan/${planId}/detalles/`)
        .then(response => response.json())
        .then(data => {
            const modalBody = document.getElementById('detallesPlanModalBody');
            modalBody.innerHTML = generarHTMLDetallesPlanDisponible(data);
            
            const modal = new bootstrap.Modal(document.getElementById('detallesPlanModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error al cargar detalles del plan:', error);
            alert('Error al cargar los detalles del plan');
        });
}

// Función para contactar negocio
function contactarNegocio(negocioId) {
    // Implementar contacto con el negocio
    alert('Función de contacto en desarrollo');
}

// Función para mostrar filtros avanzados
function mostrarFiltros() {
    const filtros = document.getElementById('filtrosAvanzados');
    filtros.style.display = filtros.style.display === 'none' ? 'block' : 'none';
}

// Función para aplicar filtros avanzados
function aplicarFiltros() {
    const categoria = document.getElementById('categoria-filtro').value;
    const ubicacion = document.getElementById('ubicacion-filtro').value;
    const precioMin = document.getElementById('precio-min-filtro').value;
    const precioMax = document.getElementById('precio-max-filtro').value;
    const duracion = document.getElementById('duracion-filtro').value;
    
    const cards = document.querySelectorAll('.plan-card-disponible');
    
    cards.forEach(card => {
        let showCard = true;
        
        if (categoria && card.dataset.categoria !== categoria) {
            showCard = false;
        }
        
        if (ubicacion && !card.dataset.ubicacion.toLowerCase().includes(ubicacion.toLowerCase())) {
            showCard = false;
        }
        
        if (precioMin && parseFloat(card.dataset.precio) < parseFloat(precioMin)) {
            showCard = false;
        }
        
        if (precioMax && parseFloat(card.dataset.precio) > parseFloat(precioMax)) {
            showCard = false;
        }
        
        if (duracion && card.dataset.duracion !== duracion) {
            showCard = false;
        }
        
        card.style.display = showCard ? '' : 'none';
    });
}

// Función para limpiar filtros
function limpiarFiltros() {
    document.getElementById('categoria-filtro').value = '';
    document.getElementById('ubicacion-filtro').value = '';
    document.getElementById('precio-min-filtro').value = '';
    document.getElementById('precio-max-filtro').value = '';
    document.getElementById('duracion-filtro').value = '';
    
    // Mostrar todas las tarjetas
    const cards = document.querySelectorAll('.plan-card-disponible');
    cards.forEach(card => {
        card.style.display = '';
    });
}

// Función para ordenar planes
function ordenarPor() {
    const modal = new bootstrap.Modal(document.getElementById('ordenamientoModal'));
    modal.show();
}

// Función para aplicar ordenamiento
function aplicarOrdenamiento() {
    const ordenamiento = document.querySelector('input[name="ordenamiento"]:checked').value;
    
    // Implementar lógica de ordenamiento
    console.log('Ordenamiento:', ordenamiento);
    
    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('ordenamientoModal'));
    modal.hide();
}

// ===== FUNCIONES AUXILIARES =====

// Función para obtener el token CSRF
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Función para generar HTML de detalles de suscripción
function generarHTMLDetalles(data) {
    return `
        <div class="detalles-suscripcion">
            <h4>Detalles de la Suscripción</h4>
            <p><strong>Cliente:</strong> ${data.cliente_nombre}</p>
            <p><strong>Plan:</strong> ${data.plan_nombre}</p>
            <p><strong>Estado:</strong> ${data.estado}</p>
            <p><strong>Fecha de inicio:</strong> ${data.fecha_inicio}</p>
            <p><strong>Fecha de vencimiento:</strong> ${data.fecha_vencimiento}</p>
            <p><strong>Precio mensual:</strong> $${data.precio_mensual}</p>
        </div>
    `;
}

// Función para generar HTML de detalles del plan
function generarHTMLDetallesPlan(data) {
    return `
        <div class="detalles-plan">
            <h4>${data.nombre}</h4>
            <p><strong>Descripción:</strong> ${data.descripcion}</p>
            <p><strong>Precio mensual:</strong> $${data.precio_mensual}</p>
            <p><strong>Duración:</strong> ${data.duracion_meses} meses</p>
            <p><strong>Estado:</strong> ${data.activo ? 'Activo' : 'Inactivo'}</p>
        </div>
    `;
}

// Función para generar HTML de detalles del plan disponible
function generarHTMLDetallesPlanDisponible(data) {
    return `
        <div class="detalles-plan-disponible">
            <h4>${data.nombre}</h4>
            <p><strong>Descripción:</strong> ${data.descripcion}</p>
            <p><strong>Precio mensual:</strong> $${data.precio_mensual}</p>
            <p><strong>Duración:</strong> ${data.duracion_meses} meses</p>
            <p><strong>Negocio:</strong> ${data.negocio_nombre}</p>
        </div>
    `;
}

// Función para cargar estadísticas
function cargarEstadisticas() {
    // Implementar carga de estadísticas
    console.log('Cargando estadísticas...');
}

// Función para cargar historial
function cargarHistorial() {
    // Implementar carga de historial
    console.log('Cargando historial...');
}

// Función para cargar información de suscripción
function cargarInfoSuscripcion(planId) {
    // Implementar carga de información para suscripción
    console.log('Cargando información para suscripción del plan:', planId);
}

// ===== INICIALIZACIÓN =====

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de suscripciones inicializado');
    
    // Inicializar tooltips si Bootstrap está disponible
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Configurar eventos de filtros si existen
    const estadoFilter = document.getElementById('estado-filter');
    if (estadoFilter) {
        estadoFilter.addEventListener('change', filtrarSuscripciones);
    }
    
    const planFilter = document.getElementById('plan-filter');
    if (planFilter) {
        planFilter.addEventListener('change', filtrarPlanes);
    }
    
    const searchFilter = document.getElementById('search-filter');
    if (searchFilter) {
        searchFilter.addEventListener('input', function() {
            if (estadoFilter) {
                filtrarSuscripciones();
            } else if (planFilter) {
                filtrarPlanes();
            }
        });
    }
});
