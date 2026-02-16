#!/usr/bin/env bash
# ============================================================
# DocSalud MX — PostgreSQL Restore Script
# Usage: ./restore-db.sh <backup_file>
# ============================================================

set -euo pipefail

BACKUP_FILE="${1:-}"
APP_DIR="/opt/docsalud-mx"
COMPOSE_FILE="docker-compose.prod.yml"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh "$APP_DIR/backups/"docsalud_backup_*.sql.gz 2>/dev/null || echo "  No backups found in $APP_DIR/backups/"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: File not found: $BACKUP_FILE"
    exit 1
fi

cd "$APP_DIR"

echo "=== DocSalud MX Database Restore ==="
echo "File: $BACKUP_FILE"
echo "Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "WARNING: This will REPLACE the current database contents."
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# 1. Create a backup of current state
echo "[1/3] Backing up current database..."
./infrastructure/scripts/backup.sh "$APP_DIR/backups" || echo "Warning: pre-restore backup failed"

# 2. Restore from backup
echo "[2/3] Restoring from backup..."
gunzip -c "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T db \
    psql -U "${POSTGRES_USER:-docsalud}" "${POSTGRES_DB:-docsalud_db}" --quiet

# 3. Verify
echo "[3/3] Verifying restore..."
TABLE_COUNT=$(docker compose -f "$COMPOSE_FILE" exec -T db \
    psql -U "${POSTGRES_USER:-docsalud}" "${POSTGRES_DB:-docsalud_db}" -t -c \
    "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

echo ""
echo "=== Restore Complete ==="
echo "Tables in database: $TABLE_COUNT"
echo ""
