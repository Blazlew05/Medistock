# Plan de Pruebas · MEDISTOCK

**Asignatura**: ASY5131 Integración de Plataformas
**Evaluación**: Parcial 2
**Versión**: 1.0
**Fecha**: 2026

---

## 1. Propósito

Validar el correcto funcionamiento del sistema MEDISTOCK en sus 3 componentes integrados (API propia, MercadoPago, sitio Cruz Amarilla) y sus 6 vistas de rol, asegurando que cumplen con los requisitos funcionales y no funcionales especificados en el caso de estudio.

---

## 2. Alcance

### 2.1 Incluido

- **Componentes integrados con BD propia** (rúbrica IL3.2): 8 componentes verificados.
  1. Catálogo público (consumible por ERPs).
  2. Autenticación con JWT y 6 roles.
  3. Panel de administración (CRUD productos).
  4. Vista de ejecutivo (stock multi-bodega + aprobación).
  5. Vista de operador logístico (priorización por urgencia).
  6. Vista de analista de finanzas (auditoría de pagos).
  7. Carrito + checkout cliente.
  8. Pasarela de pagos MercadoPago Chile.

- **APIs/Webservices integradas** (rúbrica IL3.3): 3 sistemas.
  1. API propia MEDISTOCK (productor).
  2. MercadoPago Checkout Pro (consumidor).
  3. Sitio Cruz Amarilla (consumidor de la API propia).

### 2.2 Excluido

- Sistema externo de tracking de despachos (mockeado con `tracking_simulado`).
- Notificaciones por email (fuera del scope del MVP).
- Pruebas de carga / stress testing.

---

## 3. Matriz de riesgos

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|----|--------|--------------|---------|------------|
| R1 | Webhook de MercadoPago no llega a la EC2 | Media | Alto | Validar URL pública, configurar Security Group, usar ngrok en local. Backend tolera estados manuales por analista. |
| R2 | Cliente intenta comprar con stock insuficiente | Alta | Medio | Validación en backend en `OrdenService.crear_orden`, mensaje de error claro. |
| R3 | Cliente institución paga sin aprobación | Alta | Alto | `PagoService.iniciar_pago` valida `aprobada_por_ejecutivo=True`. |
| R4 | Acceso indebido a vistas internas (cliente accede a /admin) | Alta | Alto | `AuthGuard` en frontend + `requiere_roles` en backend (defensa en profundidad). |
| R5 | Cruz Amarilla no carga si MEDISTOCK API está caído | Alta | Bajo | Sitio muestra mensaje de error sin romper, NextJS SSR con `cache: no-store`. |
| R6 | Vulnerabilidad supply chain en dependencias npm | Media | Alto | Versiones pineadas exactas (sin `^`), `npm ci` en producción, `npm audit`. |
| R7 | JWT comprometido | Baja | Alto | `SECRET_KEY` generado con `secrets.token_urlsafe(32)`, expiración 60min. |
| R8 | Datos sensibles en logs | Media | Medio | No se loguean passwords ni tokens. |

---

## 4. Criterios de cierre / aceptación

El plan se considera completo cuando:

- ✅ 100% de los casos de prueba críticos (severidad alta) pasan.
- ✅ ≥ 90% de los casos totales pasan.
- ✅ No hay defectos abiertos de severidad bloqueante.
- ✅ La aplicación es accesible públicamente desde una URL de AWS.
- ✅ Al menos un pago de extremo a extremo se completa en sandbox.

---

## 5. Casos de prueba

### 5.1 Autenticación (CP-AUTH)

| ID | Descripción | Pre-condiciones | Pasos | Resultado esperado | Severidad |
|----|-------------|-----------------|-------|--------------------|-----------|
| CP-AUTH-01 | Login válido como admin | Usuario seed cargado | POST /api/v1/auth/login con email/pass correctos | 200 + token JWT + datos usuario | Alta |
| CP-AUTH-02 | Login con password incorrecto | Usuario seed cargado | POST con password "xyz" | 401 + "Credenciales invalidas" | Alta |
| CP-AUTH-03 | Registro cliente paciente | BD inicializada | POST /api/v1/auth/registro con rol cliente_paciente | 201 + usuario creado | Alta |
| CP-AUTH-04 | Registro email duplicado | Email ya existe | POST con email repetido | 400 + mensaje claro | Media |
| CP-AUTH-05 | Acceso a /api/v1/auth/yo sin token | — | GET sin Authorization | 401 | Alta |
| CP-AUTH-06 | Acceso a /admin con rol paciente | Logueado como paciente | GET /api/v1/admin/dashboard | 403 | Crítica |

### 5.2 API Pública (CP-API)

| ID | Descripción | Pasos | Resultado esperado | Severidad |
|----|-------------|-------|--------------------|-----------|
| CP-API-01 | Listar productos sin auth | GET /api/v1/productos | 200 + array | Alta |
| CP-API-02 | Filtrar por categoría | GET /api/v1/productos?categoria=Equipamiento | 200 + solo equipamiento | Media |
| CP-API-03 | Obtener producto por código | GET /api/v1/productos/MED-JER-001 | 200 + datos | Alta |
| CP-API-04 | Producto inexistente | GET /api/v1/productos/NO-EXISTE | 404 | Media |
| CP-API-05 | Listar categorías | GET /api/v1/productos/categorias | 200 + array de strings | Baja |

### 5.3 Flujo de compra cliente paciente (CP-CLI)

| ID | Descripción | Resultado esperado | Severidad |
|----|-------------|--------------------|-----------|
| CP-CLI-01 | Agregar al carrito desde catálogo | Carrito refleja item, badge actualiza | Alta |
| CP-CLI-02 | Cambiar cantidad en carrito | Total recalcula | Media |
| CP-CLI-03 | Eliminar item del carrito | Item desaparece | Media |
| CP-CLI-04 | Crear orden con stock insuficiente | 400 + mensaje "Stock insuficiente" | Alta |
| CP-CLI-05 | Checkout completo paciente | Orden creada con `aprobada_por_ejecutivo=true` | Alta |
| CP-CLI-06 | Iniciar pago MercadoPago | Redirección a sandbox MP | Crítica |

### 5.4 Flujo cliente institución (CP-INST)

| ID | Descripción | Resultado esperado | Severidad |
|----|-------------|--------------------|-----------|
| CP-INST-01 | Crear orden como institución | Orden con `aprobada_por_ejecutivo=false` | Alta |
| CP-INST-02 | Institución intenta pagar antes de aprobación | 400 + "La orden aun no fue aprobada" | Crítica |
| CP-INST-03 | Ejecutivo aprueba orden | `aprobada_por_ejecutivo=true` | Alta |
| CP-INST-04 | Institución paga después de aprobación | Pago se procesa | Alta |

### 5.5 Operador logístico (CP-OP)

| ID | Descripción | Resultado esperado | Severidad |
|----|-------------|--------------------|-----------|
| CP-OP-01 | Listar órdenes priorizadas | Orden DESC por urgencia, luego ASC por fecha | Alta |
| CP-OP-02 | Marcar orden "en preparación" | Estado cambia | Media |
| CP-OP-03 | Despachar orden | Estado = "despachado" + tracking generado | Media |
| CP-OP-04 | Entregar orden | Estado = "entregado" | Baja |

### 5.6 Analista de finanzas (CP-FIN)

| ID | Descripción | Resultado esperado | Severidad |
|----|-------------|--------------------|-----------|
| CP-FIN-01 | Listar todos los pagos | Lista completa con estados | Alta |
| CP-FIN-02 | Auditar pago como aprobado | Estado cambia + `auditado_por` registrado | Alta |
| CP-FIN-03 | Auditar pago como rechazado | Estado = "rechazado" | Media |

### 5.7 Integración MercadoPago (CP-MP)

| ID | Descripción | Resultado esperado | Severidad |
|----|-------------|--------------------|-----------|
| CP-MP-01 | Crear preferencia | Devuelve preference_id válido | Crítica |
| CP-MP-02 | Webhook con pago aprobado | Orden pasa a "pago_confirmado" | Crítica |
| CP-MP-03 | Webhook con pago rechazado | Pago queda "rechazado", orden no avanza | Alta |
| CP-MP-04 | Pago de orden ajena | 403 | Crítica |

### 5.8 Sitio externo Cruz Amarilla (CP-EXT)

| ID | Descripción | Resultado esperado | Severidad |
|----|-------------|--------------------|-----------|
| CP-EXT-01 | Cargar home de Cruz Amarilla | Muestra productos consumidos de MEDISTOCK API | Alta |
| CP-EXT-02 | API caída | Mensaje de error, no crashea | Media |
| CP-EXT-03 | Filtrar por categoría | Solo muestra esa categoría | Media |

### 5.9 No funcionales (CP-NF)

| ID | Descripción | Criterio | Severidad |
|----|-------------|----------|-----------|
| CP-NF-01 | Tiempo de respuesta listado productos | < 500ms con 100 productos | Media |
| CP-NF-02 | Frontend responsive móvil | Navegable en viewport 375px | Alta |
| CP-NF-03 | Validación input XSS en formularios | React escapa por defecto | Alta |
| CP-NF-04 | Passwords nunca en respuesta API | UsuarioRead no incluye password_hash | Crítica |

---

## 6. Herramientas

- **Postman** — colección incluida en `postman/medistock.postman_collection.json`.
- **Swagger UI** — disponible en `/docs` para pruebas manuales.
- **Logs**: `journalctl -u medistock-backend`.

---

## 7. Estrategia de regresión

Antes de cada release:

1. Re-ejecutar todos los casos críticos (CP-AUTH-06, CP-INST-02, CP-MP-04, CP-NF-04).
2. Smoke test del flujo end-to-end completo.
3. Verificar que las 3 integraciones siguen funcionando.

---

## 8. Defectos conocidos

Ninguno bloqueante al cierre. Mejoras pendientes para versión futura:

- Notificaciones email cuando cambia estado de orden.
- Multi-currency (actualmente solo CLP).
- Integración con sistema real de tracking (Shipit / Chilexpress).
- 2FA para roles administrativos.
