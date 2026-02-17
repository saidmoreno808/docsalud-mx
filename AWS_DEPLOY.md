# AWS EC2 — Instrucciones de Despliegue

> Guia rapida para desplegar DocSalud MX en una instancia AWS EC2.
> Para la guia completa con troubleshooting, ver [docs/deployment-guide.md](docs/deployment-guide.md).

---

## Arquitectura de Produccion

```
Internet
   │
   ▼
┌──────────────────────────────────────────────────┐
│  AWS EC2  (t3.medium — Ubuntu 22.04)             │
│                                                   │
│  ┌─────────┐                                      │
│  │  NGINX  │ :80 (→HTTPS) / :443                  │
│  │  SSL    │                                      │
│  └────┬────┘                                      │
│       │                                           │
│  ┌────▼─────────┐   ┌──────────────────┐          │
│  │   Frontend   │   │    Backend API   │          │
│  │  (React SPA) │   │   (FastAPI x4)   │          │
│  │  NGINX :80   │   │   Uvicorn :8000  │          │
│  └──────────────┘   └───────┬──────────┘          │
│                             │                     │
│              ┌──────────────┼───────────┐         │
│              ▼              ▼           ▼         │
│        ┌──────────┐  ┌──────────┐ ┌────────┐     │
│        │PostgreSQL│  │  Redis   │ │Certbot │     │
│        │+pgvector │  │  Cache   │ │SSL Auto│     │
│        └──────────┘  └──────────┘ └────────┘     │
│                                                   │
│  Docker Compose (6 contenedores)                  │
└──────────────────────────────────────────────────┘
```

---

## Paso 1 — Crear la Instancia EC2

### 1.1 Ir a AWS Console > EC2 > Launch Instance

| Configuracion | Valor |
|---------------|-------|
| **Nombre** | `docsalud-mx-prod` |
| **AMI** | Ubuntu Server 22.04 LTS (64-bit x86) |
| **Tipo de instancia** | `t3.medium` (2 vCPU, 4 GB RAM) |
| **Key pair** | Crear nueva o seleccionar existente (.pem) |
| **Almacenamiento** | 30 GB gp3 |

### 1.2 Configurar Security Group

Crear un security group `docsalud-sg` con estas reglas de entrada:

```
┌───────────┬───────────┬────────┬──────────────┐
│ Tipo      │ Protocolo │ Puerto │ Origen       │
├───────────┼───────────┼────────┼──────────────┤
│ SSH       │ TCP       │ 22     │ Mi IP        │
│ HTTP      │ TCP       │ 80     │ 0.0.0.0/0    │
│ HTTPS     │ TCP       │ 443    │ 0.0.0.0/0    │
└───────────┴───────────┴────────┴──────────────┘
```

### 1.3 Asignar Elastic IP

1. EC2 > **Elastic IPs** > **Allocate Elastic IP address**
2. Seleccionar la IP creada > **Actions** > **Associate Elastic IP address**
3. Seleccionar la instancia `docsalud-mx-prod`
4. Anotar la IP: `___.___.___.___`

### 1.4 Configurar DNS

En tu registrador de dominio (o Route 53), crear registro:

```
Tipo: A
Nombre: docsalud.mx  (o tu dominio)
Valor: <Elastic IP>
TTL: 300
```

Verificar propagacion:
```bash
dig docsalud.mx +short
# Debe retornar la Elastic IP
```

---

## Paso 2 — Configurar el Servidor

### 2.1 Conectar por SSH

```bash
ssh -i ~/.ssh/tu-llave.pem ubuntu@<ELASTIC_IP>
```

### 2.2 Ejecutar el script de setup automatico

```bash
# Clonar el repositorio primero
sudo git clone https://github.com/<tu-usuario>/docsalud-mx.git /opt/docsalud-mx

# Ejecutar setup (como root)
sudo bash /opt/docsalud-mx/infrastructure/scripts/setup-server.sh
```

Esto instala automaticamente:

| Componente | Detalle |
|------------|---------|
| Docker + Compose | Engine + CLI + Compose plugin |
| NGINX | Servidor web |
| UFW Firewall | Solo puertos 22, 80, 443 |
| Swap 2 GB | Evita OOM en servidores pequenos |
| Log rotation | Rotacion diaria, 14 dias |
| Auto-updates | Parches de seguridad automaticos |
| Usuario `docsalud` | Sin privilegios root, con acceso Docker |
| Certbot | Para certificados SSL gratuitos |

### 2.3 Endurecer SSH (recomendado)

```bash
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

## Paso 3 — Configurar la Aplicacion

### 3.1 Cambiar al usuario de la aplicacion

```bash
sudo su - docsalud
cd /opt/docsalud-mx
```

### 3.2 Crear archivo de variables de entorno

```bash
cp .env.example .env
nano .env
```

### 3.3 Variables que DEBES cambiar

```bash
# ── Obligatorias ──────────────────────────────────────────

# Seguridad
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)               # Generar unico
CORS_ORIGINS=https://tu-dominio.com

# Base de datos
POSTGRES_USER=docsalud
POSTGRES_PASSWORD=$(openssl rand -hex 16)         # Generar unico
POSTGRES_DB=docsalud_db

# ── Servicios externos (si aplica) ───────────────────────

# Supabase (para RAG/vector search)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key

# OpenAI (para embeddings)
OPENAI_API_KEY=sk-tu-api-key

# Anthropic (opcional)
ANTHROPIC_API_KEY=sk-ant-tu-api-key
```

Para generar secretos seguros:
```bash
# SECRET_KEY
openssl rand -hex 32

# POSTGRES_PASSWORD
openssl rand -hex 16
```

---

## Paso 4 — Obtener Certificado SSL

### Opcion A: Script automatico (recomendado)

```bash
bash infrastructure/scripts/ssl-init.sh tu-dominio.com admin@tu-dominio.com
```

### Opcion B: Manual

```bash
# 1. Actualizar dominio en NGINX config
sed -i 's/docsalud\.mx/tu-dominio.com/g' infrastructure/nginx/nginx.conf

# 2. Levantar servicios temporalmente
docker compose -f docker-compose.prod.yml up -d nginx

# 3. Solicitar certificado
docker compose -f docker-compose.prod.yml run --rm certbot \
    certbot certonly --webroot \
    -w /var/www/certbot \
    -d tu-dominio.com \
    --email admin@tu-dominio.com \
    --agree-tos --no-eff-email

# 4. Reiniciar NGINX con SSL activo
docker compose -f docker-compose.prod.yml restart nginx
```

> El contenedor `certbot` renueva automaticamente cada 12 horas.

---

## Paso 5 — Desplegar la Aplicacion

### 5.1 Construir y levantar

```bash
cd /opt/docsalud-mx

# Construir imagenes de produccion (~10 min primera vez)
docker compose -f docker-compose.prod.yml build

# Levantar todos los servicios
docker compose -f docker-compose.prod.yml up -d
```

### 5.2 Ejecutar migraciones de base de datos

```bash
docker compose -f docker-compose.prod.yml exec backend \
    python -m alembic upgrade head
```

### 5.3 Cargar datos iniciales (opcional)

```bash
docker compose -f docker-compose.prod.yml exec backend \
    python scripts/seed_database.py
```

### 5.4 Verificar que todo esta corriendo

```bash
docker compose -f docker-compose.prod.yml ps
```

Resultado esperado:
```
NAME                       STATUS              PORTS
docsalud-db-prod           running (healthy)   5432/tcp
docsalud-redis-prod        running (healthy)   6379/tcp
docsalud-backend-prod      running (healthy)   8000/tcp
docsalud-frontend-prod     running             80/tcp
docsalud-nginx             running (healthy)   0.0.0.0:80->80, 0.0.0.0:443->443
docsalud-certbot           running
```

---

## Paso 6 — Verificar el Despliegue

```bash
# Healthcheck de la API
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

# Verificar HTTPS desde fuera
curl -I https://tu-dominio.com

# Healthcheck completo (todos los servicios)
bash infrastructure/scripts/healthcheck.sh --verbose
```

Verificar en navegador:
- **Frontend:** `https://tu-dominio.com`
- **API Docs:** `https://tu-dominio.com/docs`
- **API ReDoc:** `https://tu-dominio.com/redoc`

---

## Paso 7 — Configurar Monitoreo y Backups

### 7.1 Cron jobs (como usuario `docsalud`)

```bash
crontab -e
```

Agregar estas lineas:

```cron
# Healthcheck cada 5 minutos
*/5 * * * * /opt/docsalud-mx/infrastructure/scripts/healthcheck.sh >> /opt/docsalud-mx/logs/healthcheck.log 2>&1

# Backup diario a las 3:00 AM
0 3 * * * /opt/docsalud-mx/infrastructure/scripts/backup.sh >> /opt/docsalud-mx/logs/backup.log 2>&1

# Limpieza Docker semanal (domingos 4:00 AM)
0 4 * * 0 docker system prune -f >> /opt/docsalud-mx/logs/cleanup.log 2>&1
```

### 7.2 Verificar backups

```bash
# Listar backups existentes
ls -lh /opt/docsalud-mx/backups/

# Backup manual
bash infrastructure/scripts/backup.sh

# Restaurar un backup
bash infrastructure/scripts/restore-db.sh /opt/docsalud-mx/backups/<archivo>.sql.gz
```

---

## Paso 8 — Configurar CI/CD (GitHub Actions)

### 8.1 Generar llave SSH para deploy

```bash
# En tu maquina local
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/docsalud-deploy

# Copiar llave publica al servidor
ssh-copy-id -i ~/.ssh/docsalud-deploy.pub docsalud@<ELASTIC_IP>
```

### 8.2 Configurar GitHub Secrets

Ir a **tu repositorio > Settings > Secrets and variables > Actions** y agregar:

| Secret | Valor |
|--------|-------|
| `EC2_SSH_KEY` | Contenido de `~/.ssh/docsalud-deploy` (llave PRIVADA) |
| `EC2_HOST` | La Elastic IP del servidor |
| `EC2_USER` | `docsalud` |
| `APP_URL` | `https://tu-dominio.com` |

### 8.3 Flujo automatico

```
develop (push) ──► CI: lint + test + build
                           │
main (merge) ──────────────►  CD: deploy automatico al servidor
```

Para deploy manual sin CI/CD:
```bash
ssh docsalud@<ELASTIC_IP>
cd /opt/docsalud-mx
bash infrastructure/scripts/deploy.sh main
```

---

## Comandos Utiles (Makefile)

```bash
make docker-prod-build     # Construir imagenes produccion
make docker-prod-up        # Levantar produccion
make docker-prod-down      # Detener produccion
make docker-prod-logs      # Ver logs en tiempo real
make docker-prod-restart   # Reiniciar backend + nginx
make healthcheck           # Verificar estado de todos los servicios
make backup                # Backup manual de la base de datos
make restore-db FILE=...   # Restaurar backup
make ssl-init DOMAIN=...   # Inicializar certificado SSL
make ssl-renew             # Renovar certificado SSL
make deploy BRANCH=main    # Deploy desde un branch
```

---

## Costos Estimados

| Servicio AWS | Configuracion | Costo Mensual |
|-------------|---------------|---------------|
| EC2 | t3.medium (2 vCPU, 4GB) | ~$30 USD |
| EBS | 30 GB gp3 | ~$2.40 USD |
| Elastic IP | 1 IP asociada | $0 (gratis si esta en uso) |
| S3 (opcional) | 10 GB para backups | ~$0.25 USD |
| Route 53 (opcional) | 1 hosted zone | ~$0.50 USD |
| **Total** | | **~$33 USD/mes** |

> Para proyectos de prueba/demo, una instancia `t3.micro` (1 vCPU, 1GB, Free Tier) puede funcionar con swap activado, pero no se recomienda para carga real.

---

## Checklist de Despliegue

```
[ ] 1. Instancia EC2 creada (t3.medium, Ubuntu 22.04, 30GB)
[ ] 2. Security Group configurado (puertos 22, 80, 443)
[ ] 3. Elastic IP asignada y asociada
[ ] 4. DNS configurado (registro A apuntando a Elastic IP)
[ ] 5. DNS propagado (dig dominio.com retorna la IP)
[ ] 6. setup-server.sh ejecutado exitosamente
[ ] 7. SSH endurecido (solo llave, no root)
[ ] 8. Repositorio clonado en /opt/docsalud-mx
[ ] 9. Archivo .env creado con secretos reales
[ ] 10. Dominio actualizado en nginx.conf
[ ] 11. Certificado SSL obtenido
[ ] 12. docker compose up -d exitoso (6 contenedores running)
[ ] 13. Migraciones de DB ejecutadas
[ ] 14. Healthcheck pasando (/api/v1/health retorna "healthy")
[ ] 15. Frontend accesible via HTTPS en navegador
[ ] 16. API docs accesibles en /docs
[ ] 17. Cron jobs configurados (healthcheck + backup)
[ ] 18. GitHub Actions secrets configurados
[ ] 19. Primer backup exitoso
```

---

## En Caso de Problemas

| Problema | Solucion Rapida |
|----------|----------------|
| Backend no inicia | `docker compose -f docker-compose.prod.yml logs backend --tail=50` |
| Error 502 | `make docker-prod-restart` |
| SSL expirado | `make ssl-renew` |
| Disco lleno | `docker system prune -a` |
| DB corrupta | `make restore-db FILE=backups/ultimo_backup.sql.gz` |
| OOM (sin memoria) | Verificar swap: `free -h`, escalar a t3.large |

Para guia detallada de troubleshooting: [docs/deployment-guide.md](docs/deployment-guide.md)

---

*DocSalud MX v1.0.0 — Febrero 2026*
