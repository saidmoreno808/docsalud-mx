#!/usr/bin/env bash
# ============================================================
# DocSalud MX — Health Check & Monitoring Script
# Usage: ./healthcheck.sh [--verbose] [--notify]
# Can be run as cron job for continuous monitoring
# ============================================================

set -euo pipefail

APP_DIR="/opt/docsalud-mx"
COMPOSE_FILE="docker-compose.prod.yml"
LOG_FILE="$APP_DIR/logs/healthcheck.log"
VERBOSE="${1:-}"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

timestamp() {
    date -u '+%Y-%m-%d %H:%M:%S UTC'
}

log() {
    local msg="[$(timestamp)] $1"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

check_service() {
    local service="$1"
    local status
    status=$(docker compose -f "$APP_DIR/$COMPOSE_FILE" ps --format '{{.Status}}' "$service" 2>/dev/null || echo "not found")

    if echo "$status" | grep -qi "up\|running"; then
        echo "up"
    else
        echo "down"
    fi
}

check_api_health() {
    local response
    response=$(curl -sf --max-time 10 http://localhost:8000/api/v1/health 2>/dev/null) || {
        echo "unreachable"
        return
    }
    echo "$response"
}

check_disk_usage() {
    local usage
    usage=$(df / --output=pcent | tail -1 | tr -d ' %')
    echo "$usage"
}

check_memory_usage() {
    free -m | awk '/Mem:/ {printf "%.0f", ($3/$2)*100}'
}

check_docker_disk() {
    docker system df --format '{{.Size}}' 2>/dev/null | head -1 || echo "unknown"
}

# ── Main Health Check ───────────────────────────────────────

cd "$APP_DIR"
mkdir -p "$APP_DIR/logs"

log "=== DocSalud MX Health Check ==="

OVERALL_STATUS="healthy"
ISSUES=()

# 1. Check Docker services
log "Checking Docker services..."
for service in db redis backend frontend nginx; do
    status=$(check_service "$service")
    if [ "$status" = "up" ]; then
        log "  ${GREEN}[OK]${NC} $service: running"
    else
        log "  ${RED}[FAIL]${NC} $service: $status"
        OVERALL_STATUS="unhealthy"
        ISSUES+=("Service $service is $status")
    fi
done

# 2. Check API health endpoint
log "Checking API health..."
api_response=$(check_api_health)
if [ "$api_response" = "unreachable" ]; then
    log "  ${RED}[FAIL]${NC} API: unreachable"
    OVERALL_STATUS="unhealthy"
    ISSUES+=("API health endpoint unreachable")
else
    log "  ${GREEN}[OK]${NC} API: responding"
    if [ "$VERBOSE" = "--verbose" ]; then
        log "  Response: $api_response"
    fi
fi

# 3. Check database connectivity
log "Checking database..."
db_check=$(docker compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "${POSTGRES_USER:-docsalud}" 2>/dev/null && echo "ok" || echo "fail")
if [ "$db_check" = "ok" ]; then
    log "  ${GREEN}[OK]${NC} PostgreSQL: accepting connections"
else
    log "  ${RED}[FAIL]${NC} PostgreSQL: not ready"
    OVERALL_STATUS="unhealthy"
    ISSUES+=("PostgreSQL not accepting connections")
fi

# 4. Check Redis
log "Checking Redis..."
redis_check=$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping 2>/dev/null || echo "fail")
if [ "$redis_check" = "PONG" ]; then
    log "  ${GREEN}[OK]${NC} Redis: responding"
else
    log "  ${RED}[FAIL]${NC} Redis: not responding"
    OVERALL_STATUS="unhealthy"
    ISSUES+=("Redis not responding")
fi

# 5. Check SSL certificate expiry
log "Checking SSL certificate..."
CERT_PATH="/etc/letsencrypt/live"
if [ -d "$CERT_PATH" ]; then
    DOMAIN_DIR=$(ls "$CERT_PATH" 2>/dev/null | head -1)
    if [ -n "$DOMAIN_DIR" ] && [ -f "$CERT_PATH/$DOMAIN_DIR/fullchain.pem" ]; then
        EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_PATH/$DOMAIN_DIR/fullchain.pem" 2>/dev/null | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || echo "0")
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

        if [ "$DAYS_LEFT" -gt 30 ]; then
            log "  ${GREEN}[OK]${NC} SSL: expires in $DAYS_LEFT days"
        elif [ "$DAYS_LEFT" -gt 7 ]; then
            log "  ${YELLOW}[WARN]${NC} SSL: expires in $DAYS_LEFT days — renew soon"
            ISSUES+=("SSL certificate expires in $DAYS_LEFT days")
        else
            log "  ${RED}[FAIL]${NC} SSL: expires in $DAYS_LEFT days — URGENT"
            OVERALL_STATUS="unhealthy"
            ISSUES+=("SSL certificate expires in $DAYS_LEFT days")
        fi
    else
        log "  ${YELLOW}[WARN]${NC} SSL: no certificate found"
    fi
else
    log "  ${YELLOW}[SKIP]${NC} SSL: Let's Encrypt not configured"
fi

# 6. Check disk usage
log "Checking system resources..."
DISK_USAGE=$(check_disk_usage)
if [ "$DISK_USAGE" -lt 80 ]; then
    log "  ${GREEN}[OK]${NC} Disk: ${DISK_USAGE}% used"
elif [ "$DISK_USAGE" -lt 90 ]; then
    log "  ${YELLOW}[WARN]${NC} Disk: ${DISK_USAGE}% used — consider cleanup"
    ISSUES+=("Disk usage at ${DISK_USAGE}%")
else
    log "  ${RED}[FAIL]${NC} Disk: ${DISK_USAGE}% used — CRITICAL"
    OVERALL_STATUS="unhealthy"
    ISSUES+=("Disk usage critical at ${DISK_USAGE}%")
fi

# 7. Check memory usage
MEM_USAGE=$(check_memory_usage)
if [ "$MEM_USAGE" -lt 80 ]; then
    log "  ${GREEN}[OK]${NC} Memory: ${MEM_USAGE}% used"
elif [ "$MEM_USAGE" -lt 90 ]; then
    log "  ${YELLOW}[WARN]${NC} Memory: ${MEM_USAGE}% used"
    ISSUES+=("Memory usage at ${MEM_USAGE}%")
else
    log "  ${RED}[FAIL]${NC} Memory: ${MEM_USAGE}% used — CRITICAL"
    ISSUES+=("Memory usage critical at ${MEM_USAGE}%")
fi

# 8. Check Docker disk usage
log "  Docker disk: $(check_docker_disk)"

# ── Summary ─────────────────────────────────────────────────

log ""
if [ "$OVERALL_STATUS" = "healthy" ]; then
    log "${GREEN}=== Overall Status: HEALTHY ===${NC}"
else
    log "${RED}=== Overall Status: UNHEALTHY ===${NC}"
    log "Issues found:"
    for issue in "${ISSUES[@]}"; do
        log "  - $issue"
    done
fi

log ""

# Exit code: 0 = healthy, 1 = unhealthy
[ "$OVERALL_STATUS" = "healthy" ] && exit 0 || exit 1
