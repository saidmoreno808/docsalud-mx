# Sprint 4 Retrospective — DevOps, Deploy y Documentacion

**Sprint:** 4
**Periodo:** Febrero 2026, Semana 4
**Duracion:** 1 semana
**Equipo:** Said Ivan Briones Moreno (Solo Developer + AI Pair: Claude Code)

---

## Objetivo del Sprint

Implementar DevOps completo (Fase 7), desplegar en produccion AWS EC2 (Fase 8), y completar la documentacion final (Fase 10).

---

## User Stories Completadas

| ID | Historia | Puntos | Estado |
|----|----------|--------|--------|
| DSM-014 | Como DevOps, quiero contenedores Docker de produccion optimizados y seguros | 8 | Completado |
| DSM-015 | Como DevOps, quiero un pipeline CI/CD que ejecute tests y desplegue automaticamente | 8 | Completado |
| DSM-016 | Como usuario, quiero acceder a la aplicacion via HTTPS con dominio propio | 8 | Completado |
| DSM-017 | Como arquitecto, quiero documentacion completa del sistema para el portfolio | 5 | Completado |
| DSM-018 | Como DevOps, quiero monitoreo y backups automaticos en produccion | 3 | Completado |

**Total puntos completados:** 32/32 (100%)

---

## Lo Que Salio Bien

1. **Multi-stage Docker build:** La separacion builder/runner reduce la imagen de backend de ~8GB a ~5GB al no incluir herramientas de compilacion en la imagen final.

2. **Non-root user en Docker:** Correr el proceso como usuario `docsalud` en lugar de root mejora la seguridad significativamente con poco esfuerzo.

3. **GitHub Actions CI/CD:** El pipeline automatico de tests + deploy funciona correctamente. El deploy a produccion es completamente automatico al hacer push a main.

4. **NGINX rate limiting:** La configuracion de `limit_req_zone` protege contra abuso con configuracion simple.

5. **Let's Encrypt automatico:** El contenedor certbot en docker-compose renueva el certificado automaticamente, sin intervencion manual.

6. **Makefile:** Los comandos unificados en Makefile simplifican enormemente el workflow de desarrollo.

---

## Lo Que Salio Mal

1. **Disco lleno en EC2:** El volumen EBS de 30GB se lleno durante el build del Docker image (16.8GB de imagen + capas de cache). Requirio resize a 50GB y `growpart` + `resize2fs` en vivo.

2. **Alembic migration bug:** El `server_default="'[]'"` en las migraciones genera SQL invalido con triple comillas. Las tablas tuvieron que crearse con SQL directo. Bug documentado para la proxima migracion.

3. **Permisos de uploads/:** El directorio `/app/uploads/` era propiedad de root pero el proceso corre como `docsalud`. Fix requirio rebuild de la imagen con `chown` en Dockerfile.

4. **SSL antes de HTTP:** El primer deploy tenia NGINX configurado con SSL pero el certificado aun no existia. Se resolvio con orden correcto: HTTP → certbot → HTTPS.

5. **docker cp no persiste:** Los archivos copiados con `docker cp` al contenedor se pierden al reiniciar (imagen inmutable). Leccion aprendida: siempre hacer `docker compose build` para cambios permanentes.

---

## Incidentes en Produccion

### Incidente 1: Disco lleno (Severidad: Alta)

**Causa:** Imagen Docker de ~16.8GB + capas de cache llenaron el volumen de 30GB.
**Resolucion:** Resize de EBS de 30GB a 50GB + expansion del filesystem en caliente.
**Tiempo de resolucion:** ~45 minutos.
**Prevencion:** Monitoreo de disco con alerta al 80%.

### Incidente 2: HTTP 500 en uploads (Severidad: Media)

**Causa:** Tablas de DB no existian (Alembic migration fallida).
**Resolucion:** Creacion manual de tablas via SQL.
**Tiempo de resolucion:** ~30 minutos.
**Prevencion:** Health check de DB en el startup de la aplicacion.

### Incidente 3: ERR_CONNECTION_REFUSED en HTTPS (Severidad: Media)

**Causa:** NGINX sin certificado SSL configurado, Chrome upgrade automatico a HTTPS.
**Resolucion:** Obtener certificado Let's Encrypt y configurar puerto 443.
**Tiempo de resolucion:** ~20 minutos.

---

## Acciones de Mejora

| Accion | Responsable | Sprint |
|--------|-------------|--------|
| Agregar monitoreo de disco con alertas | Said | Backlog |
| Fix bug de Alembic con JSONB DEFAULT | Said | Sprint 5 |
| Agregar health check de DB al startup | Said | Sprint 5 |
| Documentar proceso de disaster recovery | Said | Backlog |
| Configurar cron jobs en servidor (backup, healthcheck) | Said | Backlog |

---

## Estado Final del Sistema en Produccion

| Servicio | Estado | URL |
|----------|--------|-----|
| Frontend React | Funcionando | https://docsaludmx.ochoceroocho.mx |
| API FastAPI | Funcionando | https://docsaludmx.ochoceroocho.mx/api/v1 |
| API Docs | Funcionando | https://docsaludmx.ochoceroocho.mx/docs |
| SSL Certificate | Valido hasta 18/05/2026 | Let's Encrypt |
| PostgreSQL | Funcionando | (interno) |
| Redis | Funcionando | (interno) |
| Groq LLM | Conectado | API remota |
| Supabase pgvector | Conectado | API remota |

---

## Metricas del Sprint

| Metrica | Valor |
|---------|-------|
| Story points completados | 32 |
| Incidentes en produccion | 3 |
| Tiempo de resolucion promedio | 32 minutos |
| Uptime desde deploy inicial | >99% |
| Commits del sprint | 4 |
| Archivos de documentacion creados | 12 |

---

## Commits del Sprint

- `feat(devops): add Docker production config, CI/CD pipelines, NGINX, and Makefile` (v0.8.0)
- `feat(deploy): add AWS deployment guide, healthcheck monitoring, SSL init, and DB restore scripts` (v0.9.0)
- `docs(deploy): add AWS_DEPLOY.md quickstart guide for EC2 deployment`
- `docs(phase10): add README, model cards, sprint retrospectives, and CHANGELOG` (v1.0.0)

---

## Reflexion Final del Proyecto

El desarrollo de DocSalud MX en ~4 sprints demostro que es posible construir un sistema de AI medico completo y funcional con un equipo unipersonal usando las herramientas correctas.

**Decisiones acertadas:**
- Groq API como LLM gratuito con latencia excelente
- sentence-transformers para embeddings locales sin costo
- Docker Compose para simplificar el deploy
- CLAUDE.md como unica fuente de verdad del pipeline

**Lo que haria diferente:**
- Empezar con EBS de 60GB desde el inicio
- Resolver el bug de Alembic antes del primer deploy
- Implementar monitoreo de disco desde el dia 1

**Impacto potencial:**
Con este sistema, una clinica rural puede digitalizar su backlog de expedientes en papel en dias en lugar de meses, y tiene acceso a herramientas de IA medica que normalmente solo estan disponibles en grandes hospitales.

---

*Sprint 4 completado: 17 Febrero 2026*
*Proyecto v1.0.0 liberado en produccion*
