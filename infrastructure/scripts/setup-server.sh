#!/usr/bin/env bash
# ============================================================
# DocSalud MX — EC2 Server Setup Script
# Run as root on a fresh Ubuntu 22.04 LTS instance
# ============================================================

set -euo pipefail

APP_USER="docsalud"
APP_DIR="/opt/docsalud-mx"

echo "=== DocSalud MX Server Setup ==="

# 1. Update system packages
echo "[1/10] Updating system packages..."
apt-get update && apt-get upgrade -y

# 2. Install Docker + Docker Compose
echo "[2/10] Installing Docker..."
apt-get install -y ca-certificates curl gnupg lsb-release
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

# 3. Install NGINX (host-level, optional — can also run as container)
echo "[3/10] Installing NGINX..."
apt-get install -y nginx
systemctl enable nginx

# 4. Configure firewall (UFW)
echo "[4/10] Configuring firewall..."
apt-get install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# 5. Setup swap (2GB)
echo "[5/10] Setting up swap..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "vm.swappiness=10" >> /etc/sysctl.conf
    sysctl -p
fi

# 6. Configure log rotation
echo "[6/10] Configuring log rotation..."
cat > /etc/logrotate.d/docsalud << 'LOGROTATE'
/opt/docsalud-mx/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 docsalud docsalud
    sharedscripts
}
LOGROTATE

# 7. Setup automatic security updates
echo "[7/10] Setting up automatic security updates..."
apt-get install -y unattended-upgrades
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'AUTOUPDATE'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
AUTOUPDATE

# 8. Create non-root user
echo "[8/10] Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$APP_USER"
    usermod -aG docker "$APP_USER"
fi

# 9. Create application directory
echo "[9/10] Setting up application directory..."
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/logs"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# 10. Install Certbot for SSL
echo "[10/10] Installing Certbot..."
apt-get install -y certbot python3-certbot-nginx

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Clone repo:  su - $APP_USER -c 'git clone <repo-url> $APP_DIR'"
echo "  2. Create .env:  cp $APP_DIR/.env.example $APP_DIR/.env && nano $APP_DIR/.env"
echo "  3. Get SSL cert: certbot certonly --webroot -w /var/www/certbot -d yourdomain.com"
echo "  4. Start app:    su - $APP_USER -c 'cd $APP_DIR && docker compose -f docker-compose.prod.yml up -d'"
echo ""
