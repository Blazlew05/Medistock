# Configurar MercadoPago Chile (sandbox)

Esta guía explica cómo obtener tus credenciales de prueba (sandbox) de MercadoPago Chile para que el sistema procese pagos reales en modo de prueba.

---

## Paso 1: Crear cuenta de desarrollador

1. Ve a **https://www.mercadopago.cl/developers/es**.
2. Click en "Iniciar sesión" (arriba a la derecha).
3. Si no tienes cuenta, crea una con tu correo personal. No necesitas datos bancarios para sandbox.

---

## Paso 2: Crear una aplicación

1. Una vez logueado, ve a **"Tus integraciones"** (https://www.mercadopago.cl/developers/panel/app).
2. Click en **"Crear aplicación"**.
3. Configura:
   - **Nombre**: MEDISTOCK
   - **Productos**: marcar "Pagos en línea" (Checkout Pro).
   - **Modelo de integración**: "Estás integrando para ti mismo".
4. Click "Crear aplicación".

---

## Paso 3: Obtener las credenciales de PRUEBA (sandbox)

1. En la aplicación recién creada, ve a la sección **"Credenciales de prueba"** (NO las de producción).
2. Verás dos valores:
   - **Public Key**: empieza con `TEST-...`
   - **Access Token**: empieza con `TEST-...`
3. Cópialos.

---

## Paso 4: Configurar en MEDISTOCK

Edita `backend_django/.env`:

```env
MERCADOPAGO_ACCESS_TOKEN=TEST-1234567890123456-010101-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-12345678
MERCADOPAGO_PUBLIC_KEY=TEST-12345678-0101-0101-0101-123456789012
```

Reinicia el backend:

```bash
# Local
python manage.py runserver

# En EC2
sudo systemctl restart medistock-backend
```

---

## Paso 5: Configurar la URL del webhook

MercadoPago necesita una URL pública para notificarte cuando un pago cambia de estado.

1. En el panel de MercadoPago → tu aplicación → **"Notificaciones de pago"** (Webhooks).
2. URL: `http://TU-IP-PUBLICA/api/v1/pagos/webhook`
3. Eventos a escuchar: **"Pagos"**.
4. Guardar.

**Para desarrollo local**: el webhook no llegará si solo tienes localhost. Puedes usar [ngrok](https://ngrok.com/) para exponer tu localhost temporalmente:

```bash
ngrok http 8000
# Luego usa la URL https://xxxx.ngrok.io/api/v1/pagos/webhook
```

---

## Paso 6: Probar un pago

### Tarjetas de prueba

MercadoPago Chile provee tarjetas que **no se cobran**, solo simulan:

| Marca | Número | CVV | Vencimiento |
|-------|--------|-----|-------------|
| Mastercard | `5031 7557 3453 0604` | `123` | `11/30` |
| Visa | `4168 8188 4444 7115` | `123` | `11/30` |
| American Express | `3711 803032 57522` | `1234` | `11/30` |

### Datos del titular (para forzar resultados)

Usa estos nombres en el campo "Nombre del titular" para simular distintos resultados:

| Nombre | Resultado |
|--------|-----------|
| `APRO` | Pago aprobado |
| `OTHE` | Rechazado (error general) |
| `CONT` | Pendiente |
| `CALL` | Rechazado, llamar al emisor |
| `FUND` | Rechazado por fondos insuficientes |
| `SECU` | Rechazado por código de seguridad inválido |
| `EXPI` | Rechazado por fecha vencida |
| `FORM` | Rechazado por error en formulario |

**Documento**: `12345678-5` (RUT de prueba)

---

## Paso 7: Verificar flujo completo

1. Crea una orden como cliente paciente desde el frontend.
2. Click en "Pagar con MercadoPago" → te redirige a sandbox.
3. Ingresa una tarjeta de prueba con titular `APRO`.
4. MercadoPago envía webhook → tu backend actualiza el estado a `pago_confirmado`.
5. El analista de finanzas ve el pago en `/analista`.
6. El operador ve la orden en `/operador` lista para preparar.

---

## Troubleshooting

### "Invalid access_token"
- Asegúrate de copiar el token completo (es muy largo, no se corte).
- Verifica que estés usando las credenciales de **prueba**, no las de producción.

### "Preference not found"
- Esto pasa si el token de MP no corresponde a la app donde creaste la preferencia.

### El webhook no se activa
- La URL del webhook debe ser **pública** (no localhost).
- Verifica los logs: `sudo journalctl -u medistock-backend -f` y filtra por `webhook`.

### Modo "sin credenciales"
Si no configuras `MERCADOPAGO_ACCESS_TOKEN`, el sistema corre en modo simulado:
los botones de pago redirigen a una URL falsa de éxito. Útil para demos rápidas
pero no representa un pago real.
