# Guía de Despliegue

## Requisitos previos
- Python 3.11+
- PostgreSQL 14+
- Cuenta en Stripe

## 1. Variables de entorno (producción)

Crea un archivo `.env` con:

```
SECRET_KEY=genera-una-clave-segura-con-python-secrets
DEBUG=False
DATABASE_URL=postgres://user:password@host:5432/tienda_db
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CORS_ALLOWED_ORIGINS=https://tufrontend.com

STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

Generar SECRET_KEY segura:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 2. Instalación

```bash
pip install -r requirements/production.txt
python manage.py migrate --settings=backend.settings.production
python manage.py collectstatic --settings=backend.settings.production
python manage.py createsuperuser --settings=backend.settings.production
```

## 3. Configurar Stripe Webhook

En el dashboard de Stripe → Developers → Webhooks:
- URL: `https://tudominio.com/api/v1/payments/webhook/stripe/`
- Eventos a escuchar:
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`
  - `payment_intent.canceled`

Copia el `Signing secret` y ponlo en `STRIPE_WEBHOOK_SECRET`.

## 4. Servidor con Gunicorn

```bash
gunicorn backend.wsgi:application \
  --workers 3 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 5. Nginx (configuración básica)

```nginx
server {
    listen 80;
    server_name tudominio.com;

    location /media/ {
        alias /ruta/al/proyecto/media/;
    }

    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6. Flujo de pago (frontend)

1. Cliente hace checkout → `POST /api/v1/orders/checkout/` → recibe `order_id`
2. Frontend solicita intent → `POST /api/v1/payments/create-intent/` con `order_id`
3. Backend retorna `client_secret` y `publishable_key`
4. Frontend usa Stripe.js con `client_secret` para mostrar el formulario de pago
5. Stripe confirma el pago y envía webhook a `/api/v1/payments/webhook/stripe/`
6. Backend actualiza automáticamente el estado del pedido

## 7. Crear superusuario admin

```bash
python manage.py createsuperuser
```

Luego en el admin de Django (`/admin/`) cambiar el `role` del usuario a `admin`.

## 8. Correr tests

```bash
pytest apps/ -v
```
