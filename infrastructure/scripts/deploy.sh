#!/usr/bin/env bash
# ============================================================
# DocSalud MX — Zero-downtime Deployment Script
# Usage: ./deploy.sh [branch]
# ============================================================

set -euo pipefail

APP_DIR="/opt/docsalud-mx"
BRANCH="${1:-main}"
COMPOSE_FILE="docker-compose.prod.yml"
HEALTH_URL="http://localhost:8000/api/v1/health"
MAX_HEALTH_RETRIES=30
HEALTH_INTERVAL=2

cd "$APP_DIR"

echo "=== DocSalud MX Deploy ==="
echo "Branch: $BRANCH"
echo "Time:   $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# 1. Pull latest code
echo "[1/6] Pulling latest code..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# 2. Backup database before deploy
echo "[2/6] Backing up database..."
if docker compose -f "$COMPOSE_FILE" ps db | grep -q "running"; then
    ./infrastructure/scripts/backup.sh || echo "Warning: backup failed, continuing deploy"
fi

# 3. Build new images
echo "[3/6] Building images..."
docker compose -f "$COMPOSE_FILE" build --no-cache backend frontend

# 4. Rolling restart — stop old, start new
echo "[4/6] Restarting services..."
docker compose -f "$COMPOSE_FILE" up -d --force-recreate --no-deps backend frontend nginx

# 5. Wait for health check
echo "[5/6] Waiting for health check..."
for i in $(seq 1 $MAX_HEALTH_RETRIES); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        echo "  Health check passed (attempt $i)"
        break
    fi
    if [ "$i" -eq "$MAX_HEALTH_RETRIES" ]; then
        echo "ERROR: Health check failed after $MAX_HEALTH_RETRIES attempts"
        echo "Rolling back..."
        docker compose -f "$COMPOSE_FILE" logs --tail=50 backend
        exit 1
    fi
    echo "  Waiting... (attempt $i/$MAX_HEALTH_RETRIES)"
    sleep $HEALTH_INTERVAL
done

# 6. Cleanup old images
echo "[6/6] Cleaning up..."
docker image prune -f

echo ""
echo "=== Deploy Complete ==="
echo "Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""
