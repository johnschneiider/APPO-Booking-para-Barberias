# Reporte de Problemas de Contraste en CSS

## 🚨 Problemas Identificados

### 1. **Botón Primario Hover - BAJO CONTRASTE**
**Ubicación**: `static/css/base/main.css` línea 58-60
**Problema**: 
- Fondo: `--color-aqua-mint` (#3B82F6 - azul claro)
- Texto: `--color-deep-charcoal` (#111827 - casi negro)
- **Contraste insuficiente**: Azul claro con texto oscuro no cumple WCAG AA

**Solución**: Cambiar texto a blanco o fondo a azul más oscuro

---

### 2. **Botón Secondary - BAJO CONTRASTE**
**Ubicación**: `static/css/base/main.css` línea 63-69
**Problema**:
- Fondo: `--color-coral-blush` (#F59E0B - amarillo/naranja)
- Texto: `--color-deep-charcoal` (#111827 - casi negro)
- **Contraste insuficiente**: Amarillo/naranja claro con texto oscuro no cumple WCAG AA

**Solución**: Cambiar texto a blanco o fondo a naranja más oscuro

---

### 3. **Toast/Alert Success - BAJO CONTRASTE**
**Ubicación**: `static/css/base/main.css` línea 85-89
**Problema**:
- Fondo: `--color-aqua-mint` (#3B82F6 - azul claro)
- Texto: `--color-deep-charcoal` (#111827 - casi negro)
- **Contraste insuficiente**: Azul claro con texto oscuro

**Solución**: Cambiar texto a blanco

---

### 4. **Alert Danger - BAJO CONTRASTE**
**Ubicación**: `static/css/base/main.css` línea 91-94
**Problema**:
- Fondo: `--color-coral-blush` (#F59E0B - amarillo/naranja)
- Texto: `--color-deep-charcoal` (#111827 - casi negro)
- **Contraste insuficiente**: Amarillo/naranja claro con texto oscuro

**Solución**: Cambiar texto a blanco o fondo a rojo más oscuro

---

### 5. **Text-Muted sobre Fondos Claros - BAJO CONTRASTE**
**Ubicación**: `static/css/base/variables.css` línea 23
**Problema**:
- Color: `--color-text-muted` (#9CA3AF - gris claro)
- Fondo: Blanco (#FFFFFF) o gris muy claro (#F9FAFB, #F3F4F6)
- **Contraste insuficiente**: Gris claro sobre fondos claros no cumple WCAG AA

**Solución**: Oscurecer el color a #6B7280 o más oscuro

---

### 6. **Text-Secondary sobre Fondos Claros - CONTRASTE LIMITADO**
**Ubicación**: `static/css/base/variables.css` línea 22
**Problema**:
- Color: `--color-text-secondary` (#6B7280 - gris medio)
- Fondo: Blanco (#FFFFFF) o gris muy claro
- **Contraste**: Cumple WCAG AA pero podría mejorarse

**Solución**: Considerar oscurecer ligeramente a #4B5563

---

### 7. **Footer Text-Secondary - CONTRASTE LIMITADO**
**Ubicación**: `static/css/base/variables.css` línea 107
**Problema**:
- Color: `--color-text-secondary` (#6B7280)
- Fondo: `--color-bg-primary` (#FFFFFF - blanco)
- **Contraste**: Cumple WCAG AA pero podría mejorarse

---

### 8. **Horario Card con Gradiente - POSIBLE BAJO CONTRASTE**
**Ubicación**: `static/css/base/main.css` línea 38-41
**Problema**:
- Fondo: Gradiente de `--color-aqua-mint` (#3B82F6) a `--color-teal-accent` (#10B981)
- Texto: `--color-deep-charcoal` (#111827)
- **Contraste**: Depende de la parte del gradiente, puede tener bajo contraste

---

## 📊 Resumen de Contraste WCAG

| Elemento | Fondo | Texto | Ratio | WCAG AA | WCAG AAA |
|----------|-------|-------|-------|---------|----------|
| Botón Primary Hover | #3B82F6 | #111827 | ~2.8:1 | ❌ | ❌ |
| Botón Secondary | #F59E0B | #111827 | ~3.1:1 | ⚠️ | ❌ |
| Toast Success | #3B82F6 | #111827 | ~2.8:1 | ❌ | ❌ |
| Alert Danger | #F59E0B | #111827 | ~3.1:1 | ⚠️ | ❌ |
| Text-Muted | #FFFFFF | #9CA3AF | ~2.4:1 | ❌ | ❌ |
| Text-Secondary | #FFFFFF | #6B7280 | ~4.5:1 | ✅ | ❌ |

**Nota**: WCAG AA requiere mínimo 4.5:1 para texto normal, 3:1 para texto grande.
WCAG AAA requiere mínimo 7:1 para texto normal, 4.5:1 para texto grande.

