# DocSalud MX — Guia de Despliegue en AWS EC2

> Guia completa paso a paso para desplegar DocSalud MX en produccion.

---

## Tabla de Contenidos

1. [Requisitos Previos](#1-requisitos-previos)
2. [Crear Instancia EC2](#2-crear-instancia-ec2)
3. [Configurar Dominio y DNS](#3-configurar-dominio-y-dns)
4. [Setup Inicial del Servidor](#4-setup-inicial-del-servidor)
5. [Clonar y Configurar el Proyecto](#5-clonar-y-configurar-el-proyecto)
6. [Configurar Variables de Entorno](#6-configurar-variables-de-entorno)
7. [Obtener Certificado SSL](#7-obtener-certificado-ssl)
8. [Primer Despliegue](#8-primer-despliegue)
9. [Verificar el Despliegue](#9-verificar-el-despliegue)
10. [Configurar CI/CD con GitHub Actions](#10-configurar-cicd-con-github-actions)
11. [Monitoreo y Mantenimiento](#11-monitoreo-y-mantenimiento)
12. [Backups y Restauracion](#12-backups-y-restauracion)
13. [Troubleshooting](#13-troubleshooting)
14. [Escalar la Infraestructura](#14-escalar-la-infraestructura)

---

## 1. Requisitos Previos

### Cuentas necesarias
- **AWS Account** con acceso a EC2, S3, Route 53
- **Dominio** registrado (ej: docsalud.mx)
- **GitHub** con acceso al repositorio
- **Supabase** proyecto creado (para pgvector)
- **OpenAI** API key (para embeddings y RAG)

### Herramientas locales
```bash
# AWS CLI
aws --version   # >= 2.x

# SSH key pair generado
ls ~/.ssh/id_rsa.pub

# Git configurado
git remote -v
```

### Costos estimados (mensual)
| Recurso | Tipo | Costo Aprox. |
|---------|------|-------------|
| EC2 | t3.medium (2 vCPU, 4GB RAM) | ~$30 USD |
| EBS | 30GB gp3 | ~$2.40 USD |
| S3 | 10GB storage | ~$0.25 USD |
| Route 53 | Hosted zone | ~$0.50 USD |
| **Total** | | **~$33 USD/mes** |

---

## 2. Crear Instancia EC2

### 2.1 — Desde la consola AWS

1. Ir a **EC2 > Launch Instance**
2. Configurar:

| Parametro | Valor |
|-----------|-------|
| Name | docsalud-mx-prod |
| AMI | Ubuntu Server 22.04 LTS (64-bit x86) |
| Instance type | t3.medium (minimo) |
| Key pair | Crear nuevo o usar existente |
| Network | VPC default |
| Security Group | Ver reglas abajo |
| Storage | 30 GB gp3 |

### 2.2 — Security Group (Firewall AWS)

| Tipo | Protocolo | Puerto | Origen | Descripcion |
|------|-----------|--------|--------|-------------|
| SSH | TCP | 22 | Tu IP /32 | Acceso SSH |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web HTTP |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Web HTTPS |

### 2.3 — Elastic IP (IP estatica)

1. EC2 > Elastic IPs > Allocate
2. Associate con la instancia creada
3. Anotar la IP: `___.___.___.__`

---

## 3. Configurar Dominio y DNS

### Con Route 53 (recomendado)

1. Route 53 > Hosted zones > Create hosted zone: `docsalud.mx`
2. Crear registro A:
   - Name: `docsalud.mx`
   - Type: A
   - Value: `<Elastic IP>`
   - TTL: 300
3. Crear registro A para www:
   - Name: `www.docsalud.mx`
   - Type: CNAME
   - Value: `docsalud.mx`

### Con otro registrador DNS

Configurar registro A apuntando a la Elastic IP.

### Verificar DNS
```bash
# Esperar propagacion (5-30 minutos)
dig docsalud.mx +short
# Debe mostrar la Elastic IP
```

---

## 4. Setup Inicial del Servidor

### 4.1 — Conectar por SSH
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@<ELASTIC_IP>
```

### 4.2 — Ejecutar script de setup
```bash
# Descargar y ejecutar el script
sudo bash -c 'curl -fsSL https://raw.githubusercontent.com/<tu-repo>/main/infrastructure/scripts/setup-server.sh | bash'

# O si ya clonaste el repo:
sudo bash /opt/docsalud-mx/infrastructure/scripts/setup-server.sh
```

El script automaticamente:
- Actualiza paquetes del sistema
- Instala Docker y Docker Compose
- Instala NGINX
- Configura firewall (UFW: solo puertos 22, 80, 443)
- Crea swap de 2GB (importante para servidores pequenos)
- Configura rotacion de logs
- Habilita actualizaciones automaticas de seguridad
- Crea usuario `docsalud` sin privilegios root
- Instala Certbot para SSL

### 4.3 — Configurar SSH solo con llave
```bash
# Editar configuracion SSH
sudo nano /etc/ssh/sshd_config

# Cambiar estas lineas:
PasswordAuthentication no
PermitRootLogin no

# Reiniciar SSH
sudo systemctl restart sshd
```

---

## 5. Clonar y Configurar el Proyecto

```bash
# Cambiar al usuario de la aplicacion
sudo su - docsalud

# Clonar repositorio
git clone https://github.com/<tu-usuario>/docsalud-mx.git /opt/docsalud-mx

# Entrar al directorio
cd /opt/docsalud-mx

# Verificar estructura
ls -la
```

---

## 6. Configurar Variables de Entorno

### 6.1 — Crear archivo .env
```bash
cp .env.example .env
nano .env
```

### 6.2 — Variables criticas a configurar

```bash
# === App ===
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=<generar-con: openssl rand -hex 32>
CORS_ORIGINS=https://docsalud.mx,https://www.docsalud.mx

# === Database ===
POSTGRES_USER=docsalud
POSTGRES_PASSWORD=<generar-con: openssl rand -hex 16>
POSTGRES_DB=docsalud_db

# === Supabase ===
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# === OpenAI ===
OPENAI_API_KEY=sk-your-key

# === Anthropic (opcional) ===
ANTHROPIC_API_KEY=sk-ant-your-key
```

### 6.3 — Generar secretos seguros
```bash
# Para SECRET_KEY
openssl rand -hex 32

# Para POSTGRES_PASSWORD
openssl rand -hex 16
```

> **IMPORTANTE:** Nunca commitear el archivo `.env`. Esta en `.gitignore`.

---

## 7. Obtener Certificado SSL

### Opcion A: Usando el script incluido
```bash
bash infrastructure/scripts/ssl-init.sh docsalud.mx admin@docsalud.mx
```

### Opcion B: Manual con Certbot
```bash
# 1. Iniciar solo NGINX para el ACME challenge
docker compose -f docker-compose.prod.yml up -d nginx

# 2. Obtener certificado
docker compose -f docker-compose.prod.yml run --rm certbot \
    certbot certonly --webroot \
    -w /var/www/certbot \
    -d docsalud.mx \
    --email admin@docsalud.mx \
    --agree-tos --no-eff-email

# 3. Reiniciar NGINX con SSL
docker compose -f docker-compose.prod.yml restart nginx
```

### Verificar certificado
```bash
curl -I https://docsalud.mx
# Debe mostrar HTTP/2 200 (o redirect)
```

### Renovacion automatica
El contenedor `certbot` incluido en `docker-compose.prod.yml` renueva automaticamente cada 12 horas. No se requiere configuracion adicional.

---

## 8. Primer Despliegue

### 8.1 — Build y levantar servicios
```bash
cd /opt/docsalud-mx

# Construir imagenes (primera vez tarda ~10 minutos)
docker compose -f docker-compose.prod.yml build

# Levantar todos los servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f
```

### 8.2 — Ejecutar migraciones de DB
```bash
docker compose -f docker-compose.prod.yml exec backend \
    python -m alembic upgrade head
```

### 8.3 — Seed de datos iniciales (opcional)
```bash
docker compose -f docker-compose.prod.yml exec backend \
    python scripts/seed_database.py
```

### 8.4 — Verificar que todo esta corriendo
```bash
# Ver estado de contenedores
docker compose -f docker-compose.prod.yml ps

# Esperado:
# docsalud-db-prod        running (healthy)
# docsalud-redis-prod     running (healthy)
# docsalud-backend-prod   running (healthy)
# docsalud-frontend-prod  running
# docsalud-nginx          running (healthy)
# docsalud-certbot        running
```

---

## 9. Verificar el Despliegue

### 9.1 — Healthcheck
```bash
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
```

Respuesta esperada:
```json
{
    "status": "healthy",
    "components": {
        "database": "up",
        "vector_store": "up",
        "ocr_engine": "up",
        "ml_models": "loaded",
        "llm_api": "reachable"
    },
    "version": "1.0.0"
}
```

### 9.2 — Verificar HTTPS
```bash
curl -I https://docsalud.mx
```

### 9.3 — Verificar frontend
Abrir en navegador: `https://docsalud.mx`

### 9.4 — Verificar API docs
Abrir: `https://docsalud.mx/docs` (Swagger UI)

### 9.5 — Script de healthcheck completo
```bash
bash infrastructure/scripts/healthcheck.sh --verbose
```

---

## 10. Configurar CI/CD con GitHub Actions

### 10.1 — Secrets de GitHub

Ir a **Settings > Secrets and variables > Actions** y agregar:

| Secret | Valor | Descripcion |
|--------|-------|-------------|
| `EC2_SSH_KEY` | Contenido de la llave privada SSH | Para conectar al servidor |
| `EC2_HOST` | `<Elastic IP>` | IP del servidor |
| `EC2_USER` | `docsalud` | Usuario SSH |
| `APP_URL` | `https://docsalud.mx` | URL publica |

### 10.2 — Configurar llave SSH

```bash
# En tu maquina local, generar llave para deploy
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/docsalud-deploy

# Copiar la llave publica al servidor
ssh-copy-id -i ~/.ssh/docsalud-deploy.pub docsalud@<ELASTIC_IP>

# Copiar la llave PRIVADA como secret en GitHub
cat ~/.ssh/docsalud-deploy
# Pegar en GitHub Secret: EC2_SSH_KEY
```

### 10.3 — Flujo de CI/CD

```
Push a develop → CI (lint, test, build)
                                 ↓
PR a main → CI + Review → Merge → CD (deploy automatico)
```

### 10.4 — Deploy manual (sin CI/CD)
```bash
ssh docsalud@<ELASTIC_IP>
cd /opt/docsalud-mx
bash infrastructure/scripts/deploy.sh main
```

---

## 11. Monitoreo y Mantenimiento

### 11.1 — Cron jobs recomendados

```bash
# Editar crontab del usuario docsalud
crontab -e

# Agregar:
# Healthcheck cada 5 minutos
*/5 * * * * /opt/docsalud-mx/infrastructure/scripts/healthcheck.sh >> /opt/docsalud-mx/logs/healthcheck.log 2>&1

# Backup diario a las 3 AM
0 3 * * * /opt/docsalud-mx/infrastructure/scripts/backup.sh >> /opt/docsalud-mx/logs/backup.log 2>&1

# Limpieza de Docker semanal (domingos 4 AM)
0 4 * * 0 docker system prune -f >> /opt/docsalud-mx/logs/cleanup.log 2>&1
```

### 11.2 — Ver logs

```bash
# Logs del backend
docker compose -f docker-compose.prod.yml logs -f backend

# Logs de NGINX (acceso)
docker compose -f docker-compose.prod.yml logs -f nginx

# Logs del healthcheck
tail -f /opt/docsalud-mx/logs/healthcheck.log

# Logs de todos los servicios
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

### 11.3 — Monitoreo de recursos
```bash
# Uso de CPU/memoria por contenedor
docker stats

# Espacio en disco
df -h

# Docker disk usage
docker system df
```

### 11.4 — Reiniciar un servicio
```bash
# Solo el backend
docker compose -f docker-compose.prod.yml restart backend

# Todo el stack
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

---

## 12. Backups y Restauracion

### 12.1 — Backup manual
```bash
bash infrastructure/scripts/backup.sh
# Output: /opt/docsalud-mx/backups/docsalud_backup_YYYYMMDD_HHMMSS.sql.gz
```

### 12.2 — Listar backups
```bash
ls -lh /opt/docsalud-mx/backups/
```

### 12.3 — Restaurar desde backup
```bash
bash infrastructure/scripts/restore-db.sh /opt/docsalud-mx/backups/docsalud_backup_20260215_030000.sql.gz
```

### 12.4 — Copiar backup a S3 (opcional)
```bash
aws s3 cp /opt/docsalud-mx/backups/ s3://docsalud-mx-backups/ --recursive
```

### Retencion
- Backups locales: 30 dias (automatico)
- Backups en S3: configurar lifecycle policy

---

## 13. Troubleshooting

### El backend no inicia
```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs backend --tail=50

# Verificar que la DB esta lista
docker compose -f docker-compose.prod.yml exec db pg_isready

# Entrar al contenedor para debug
docker compose -f docker-compose.prod.yml exec backend bash
```

### Error 502 Bad Gateway
```bash
# NGINX no puede conectar al backend
# Verificar que el backend esta healthy
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs backend --tail=20

# Reiniciar
docker compose -f docker-compose.prod.yml restart backend nginx
```

### Certificado SSL expirado
```bash
# Renovar manualmente
docker compose -f docker-compose.prod.yml run --rm certbot certbot renew
docker compose -f docker-compose.prod.yml restart nginx
```

### Disco lleno
```bash
# Ver que ocupa espacio
du -sh /var/lib/docker/*
docker system df

# Limpiar
docker system prune -a --volumes
# CUIDADO: esto elimina imagenes y volumenes no usados
```

### Contenedor se reinicia constantemente
```bash
# Ver logs del contenedor
docker compose -f docker-compose.prod.yml logs <servicio> --tail=100

# Ver eventos de Docker
docker events --since 1h --filter container=docsalud-backend-prod
```

### Base de datos corrupta
```bash
# 1. Detener el backend
docker compose -f docker-compose.prod.yml stop backend

# 2. Restaurar ultimo backup
bash infrastructure/scripts/restore-db.sh <backup_file>

# 3. Reiniciar
docker compose -f docker-compose.prod.yml start backend
```

---

## 14. Escalar la Infraestructura

### Cuando escalar verticalmente (mas recursos)
- CPU > 80% sostenido
- Memoria > 85% sostenido
- Tiempos de respuesta > 2 segundos

```
t3.medium (4GB) → t3.large (8GB) → t3.xlarge (16GB)
```

### Cuando considerar escalar horizontalmente
- Mas de 100 usuarios concurrentes
- Necesidad de alta disponibilidad
- Separar backend de ML processing

### Arquitectura escalada
```
                    ┌── EC2 (Backend API)
ALB ── Route 53 ──┤
                    └── EC2 (ML Workers)

RDS PostgreSQL (managed)
ElastiCache Redis (managed)
S3 (documentos)
```

---

## Checklist de Despliegue

- [ ] Instancia EC2 creada con security group correcto
- [ ] Elastic IP asociada
- [ ] DNS configurado y propagado
- [ ] Script setup-server.sh ejecutado
- [ ] Repositorio clonado en /opt/docsalud-mx
- [ ] Archivo .env configurado con secretos reales
- [ ] Certificado SSL obtenido
- [ ] docker-compose up exitoso
- [ ] Migraciones de DB ejecutadas
- [ ] Healthcheck pasando
- [ ] Frontend accesible via HTTPS
- [ ] API docs accesibles en /docs
- [ ] GitHub Actions secrets configurados
- [ ] Cron jobs de backup y healthcheck activos
- [ ] SSH con solo llave (password deshabilitado)

---

*Ultima actualizacion: Febrero 2026*
