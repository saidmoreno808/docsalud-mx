#!/usr/bin/env bash
# ============================================================
# DocSalud MX — SSL Certificate Initialization
# Usage: ./ssl-init.sh <domain> [email]
# ============================================================

set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-admin@$DOMAIN}"
APP_DIR="/opt/docsalud-mx"
COMPOSE_FILE="docker-compose.prod.yml"

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain> [email]"
    echo "Example: $0 docsalud.mx admin@docsalud.mx"
    exit 1
fi

cd "$APP_DIR"

echo "=== DocSalud MX SSL Setup ==="
echo "Domain: $DOMAIN"
echo "Email:  $EMAIL"
echo ""

# 1. Update NGINX config with the actual domain
echo "[1/4] Updating NGINX configuration..."
sed -i "s/docsalud\.mx/$DOMAIN/g" infrastructure/nginx/nginx.conf

# 2. Start NGINX with HTTP-only temporarily for ACME challenge
echo "[2/4] Starting services for ACME challenge..."

# Create a temporary NGINX config that only serves HTTP (for initial cert)
cat > /tmp/nginx-temp.conf << 'TEMPNGINX'
events { worker_connections 1024; }
http {
    server {
        listen 80;
        server_name _;
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        location / {
            return 200 "Waiting for SSL setup...";
            add_header Content-Type text/plain;
        }
    }
}
TEMPNGINX

# Start only nginx with temp config and certbot volumes
docker compose -f "$COMPOSE_FILE" up -d nginx

# 3. Request certificate
echo "[3/4] Requesting SSL certificate from Let's Encrypt..."
docker compose -f "$COMPOSE_FILE" run --rm certbot \
    certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d "$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal

# 4. Restart NGINX with full SSL config
echo "[4/4] Restarting NGINX with SSL..."
docker compose -f "$COMPOSE_FILE" restart nginx

echo ""
echo "=== SSL Setup Complete ==="
echo "Certificate installed for: $DOMAIN"
echo ""
echo "Auto-renewal is handled by the certbot container."
echo "Test: curl -I https://$DOMAIN"
echo ""
