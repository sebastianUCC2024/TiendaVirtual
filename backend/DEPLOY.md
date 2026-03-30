# Guía de Despliegue Gratuito

## Stack
- Railway → Django + PostgreSQL (gratis con $5 crédito mensual)
- Cloudinary → imágenes de productos (gratis 25GB)
- GitHub → repositorio del código

---

## Antes de empezar — cuentas necesarias

1. https://railway.app → crear cuenta (con GitHub)
2. https://cloudinary.com → crear cuenta gratis
3. https://github.com → subir el código

---

## Paso 1 — Subir el código a GitHub

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/tienda-backend.git
git push -u origin main
```

---

## Paso 2 — Obtener credenciales de Cloudinary

1. Entra a https://cloudinary.com y crea tu cuenta
2. En el Dashboard verás:
   - Cloud name
   - API Key
   - API Secret
3. Guárdalos, los necesitas en el paso 4

---

## Paso 3 — Crear proyecto en Railway

1. Entra a https://railway.app
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu cuenta de GitHub y selecciona el repositorio
5. Railway detecta el `Procfile` automáticamente

---

## Paso 4 — Agregar PostgreSQL en Railway

1. Dentro de tu proyecto en Railway, click en "New Service"
2. Selecciona "Database" → "PostgreSQL"
3. Railway crea la base de datos y genera la variable `DATABASE_URL` automáticamente
4. Esa variable se inyecta sola en tu servicio Django — no tienes que copiarla

---

## Paso 5 — Variables de entorno en Railway

En tu servicio Django → pestaña "Variables" → agrega estas:

```
DJANGO_SETTINGS_MODULE = backend.settings.production
SECRET_KEY             = (genera con: python -c "import secrets; print(secrets.token_urlsafe(50))")
DEBUG                  = False
ALLOWED_HOSTS          = tu-app.up.railway.app
CORS_ALLOWED_ORIGINS   = https://tu-frontend.vercel.app

STRIPE_SECRET_KEY      = sk_live_... (o sk_test_... para pruebas)
STRIPE_PUBLISHABLE_KEY = pk_live_...
STRIPE_WEBHOOK_SECRET  = whsec_... (lo obtienes en el paso 7)

CLOUDINARY_CLOUD_NAME  = tu_cloud_name
CLOUDINARY_API_KEY     = tu_api_key
CLOUDINARY_API_SECRET  = tu_api_secret
```

Railway inyecta `DATABASE_URL` automáticamente desde el servicio PostgreSQL.

---

## Paso 6 — Crear superusuario admin

Railway tiene una terminal integrada. En tu servicio Django → pestaña "Deploy" → "Railway Shell":

```bash
python manage.py createsuperuser --settings=backend.settings.production
```

Luego entra al admin en `https://tu-app.up.railway.app/admin/`, busca el usuario y cambia su `role` a `admin`.

---

## Paso 7 — Configurar Stripe Webhook

1. Entra a https://dashboard.stripe.com → Developers → Webhooks
2. Click "Add endpoint"
3. URL: `https://tu-app.up.railway.app/api/v1/payments/webhook/stripe/`
4. Eventos a seleccionar:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
5. Click "Add endpoint"
6. Copia el "Signing secret" (empieza con `whsec_`)
7. Pégalo en Railway como `STRIPE_WEBHOOK_SECRET`

---

## Paso 8 — Verificar que todo funciona

```
GET https://tu-app.up.railway.app/api/v1/catalog/products/
→ debe retornar { count: 0, results: [] }

GET https://tu-app.up.railway.app/admin/
→ debe mostrar el panel de Django
```

---

## Flujo de pago para el frontend

```
1. POST /api/v1/orders/checkout/
   body: { address_id, coupon_code (opcional) }
   → retorna: { order_number, total, ... }

2. POST /api/v1/payments/create-intent/
   body: { order_id }
   → retorna: { client_secret, publishable_key }

3. Frontend usa Stripe.js con client_secret
   → el cliente ingresa su tarjeta

4. Stripe confirma → llama al webhook automáticamente
   → el pedido pasa a payment_approved sin intervención manual
```

---

## Actualizar el backend (re-deploy)

Cada push a `main` en GitHub dispara un deploy automático en Railway:

```bash
git add .
git commit -m "descripción del cambio"
git push origin main
```

Railway corre las migraciones automáticamente gracias al comando `release` en el `Procfile`.

---

## Límites del tier gratuito de Railway

- $5 USD de crédito mensual (se renueva cada mes)
- Suficiente para un proyecto pequeño/mediano en producción
- Si superas el crédito, el servicio se pausa hasta el siguiente mes
- PostgreSQL incluido sin costo adicional dentro del crédito

## Límites de Cloudinary gratis

- 25 GB de almacenamiento
- 25 GB de ancho de banda mensual
- Más que suficiente para una tienda de ropa en etapa inicial
