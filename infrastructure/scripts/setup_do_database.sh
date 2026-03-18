#!/usr/bin/env bash
# ============================================================
# setup_do_database.sh — Crea y configura DO Managed PostgreSQL
# Uso: bash infrastructure/scripts/setup_do_database.sh
# Requiere: doctl autenticado (doctl auth init)
# ============================================================
set -euo pipefail

DB_NAME="docsalud-pg"
DB_ENGINE="pg"
DB_VERSION="16"
DB_SIZE="db-s-1vcpu-2gb"
DB_REGION="nyc3"

echo "========================================================"
echo "  ClinicaIA — Setup DO Managed PostgreSQL"
echo "========================================================"

# 1. Crear la base de datos managed
echo ""
echo "[1/4] Creando DO Managed PostgreSQL '$DB_NAME'..."
doctl databases create "$DB_NAME" \
  --engine "$DB_ENGINE" \
  --version "$DB_VERSION" \
  --size "$DB_SIZE" \
  --region "$DB_REGION" \
  --num-nodes 1

echo "  Base de datos '$DB_NAME' creada. Esperando que esté ONLINE..."

# 2. Esperar a que esté ONLINE (hasta 10 minutos)
MAX_WAIT=60
COUNT=0
while true; do
  STATUS=$(doctl databases list --format Name,Status --no-header \
    | grep "^$DB_NAME" | awk '{print $2}' || true)

  if [ "$STATUS" = "online" ]; then
    echo "  ✅ Base de datos ONLINE."
    break
  fi

  COUNT=$((COUNT + 1))
  if [ "$COUNT" -ge "$MAX_WAIT" ]; then
    echo "  ⚠️  Timeout esperando. Verifica manualmente con: doctl databases list"
    break
  fi

  echo "  Estado actual: '$STATUS'. Reintentando en 10s... ($COUNT/$MAX_WAIT)"
  sleep 10
done

# 3. Obtener el connection string
echo ""
echo "[2/4] Obteniendo connection string..."
DB_ID=$(doctl databases list --format Name,ID --no-header \
  | grep "^$DB_NAME" | awk '{print $2}')

if [ -z "$DB_ID" ]; then
  echo "  ⚠️  No se pudo obtener el ID. Corre: doctl databases list"
else
  CONNECTION_URI=$(doctl databases connection "$DB_ID" --format URI --no-header 2>/dev/null || echo "")
  if [ -n "$CONNECTION_URI" ]; then
    # Adaptar para asyncpg
    ASYNCPG_URL="${CONNECTION_URI/postgresql:\/\//postgresql+asyncpg://}"
    echo ""
    echo "  Connection string (asyncpg):"
    echo "  $ASYNCPG_URL"
    echo ""
    echo "  👉 Agrega esto a tu .env y a los secrets de DO App Platform:"
    echo "     DATABASE_URL=$ASYNCPG_URL"
  fi
fi

# 4. Instrucciones para habilitar pgvector
echo ""
echo "[3/4] Habilitar extensión pgvector:"
echo "  Conéctate a la DB y ejecuta:"
echo ""
echo "    CREATE EXTENSION IF NOT EXISTS vector;"
echo ""
echo "  Puedes conectarte con:"
if [ -n "${DB_ID:-}" ]; then
  echo "    doctl databases db list $DB_ID"
  echo "    psql \"\$DATABASE_URL\""
fi

# 5. Instrucciones finales
echo ""
echo "[4/4] Próximos pasos:"
echo "  1. Agrega DATABASE_URL a los secrets de DO App Platform:"
echo "     https://cloud.digitalocean.com/apps → Settings → Environment Variables"
echo "  2. Ejecuta migraciones Alembic:"
echo "     make migrate"
echo "  3. Verifica pgvector:"
echo "     psql \"\$DATABASE_URL\" -c \"SELECT * FROM pg_extension WHERE extname='vector';\""
echo ""
echo "  ✅ Setup completo."
