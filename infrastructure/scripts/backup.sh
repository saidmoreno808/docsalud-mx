#!/usr/bin/env bash
# ============================================================
# DocSalud MX — PostgreSQL Backup Script
# Usage: ./backup.sh [backup_dir]
# ============================================================

set -euo pipefail

APP_DIR="/opt/docsalud-mx"
BACKUP_DIR="${1:-$APP_DIR/backups}"
COMPOSE_FILE="docker-compose.prod.yml"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="docsalud_backup_${TIMESTAMP}.sql.gz"

cd "$APP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "=== DocSalud MX Database Backup ==="
echo "Time:   $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Output: $BACKUP_DIR/$BACKUP_FILE"

# Run pg_dump inside the container and compress
docker compose -f "$COMPOSE_FILE" exec -T db \
    pg_dump -U "${POSTGRES_USER:-docsalud}" "${POSTGRES_DB:-docsalud_db}" \
    --no-owner --no-privileges --clean --if-exists \
    | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Verify backup
BACKUP_SIZE=$(stat -f%z "$BACKUP_DIR/$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_DIR/$BACKUP_FILE")
if [ "$BACKUP_SIZE" -lt 100 ]; then
    echo "ERROR: Backup file too small ($BACKUP_SIZE bytes), may be corrupted"
    rm -f "$BACKUP_DIR/$BACKUP_FILE"
    exit 1
fi

echo "Backup created: $BACKUP_FILE ($(numfmt --to=iec $BACKUP_SIZE))"

# Remove old backups
echo "Removing backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "docsalud_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

REMAINING=$(find "$BACKUP_DIR" -name "docsalud_backup_*.sql.gz" | wc -l)
echo "Backups remaining: $REMAINING"

echo "=== Backup Complete ==="
