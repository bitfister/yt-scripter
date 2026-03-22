#!/bin/bash
# YT Scripter — Lightsail bootstrap script
# This runs automatically on first boot via --user-data
set -euo pipefail

REPO="https://github.com/bitfister/yt-scripter.git"
APP_DIR="/home/ubuntu/yt-scripter"
USER="ubuntu"

export DEBIAN_FRONTEND=noninteractive

# --- System packages ---
apt-get update -y
apt-get install -y python3 python3-pip python3-venv nginx git

# --- Clone repo ---
if [ ! -d "$APP_DIR" ]; then
    sudo -u "$USER" git clone "$REPO" "$APP_DIR"
fi

# --- Python virtual env + deps ---
cd "$APP_DIR"
sudo -u "$USER" python3 -m venv venv
sudo -u "$USER" bash -c "source venv/bin/activate && pip install -r requirements.txt"

# --- Create placeholder .env (user must fill in API key) ---
if [ ! -f "$APP_DIR/.env" ]; then
    sudo -u "$USER" cat > "$APP_DIR/.env" << 'ENVEOF'
ANTHROPIC_API_KEY=sk-ant-REPLACE-ME
ENVEOF
fi

# --- Gunicorn systemd service ---
cat > /etc/systemd/system/yt-scripter.service << 'SVCEOF'
[Unit]
Description=YT Scripter
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/yt-scripter
ExecStart=/home/ubuntu/yt-scripter/venv/bin/gunicorn -w 2 -b 127.0.0.1:5050 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable yt-scripter
systemctl start yt-scripter

# --- Nginx reverse proxy ---
cat > /etc/nginx/sites-available/yt-scripter << 'NGXEOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
NGXEOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/yt-scripter /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

echo "=== YT Scripter setup complete ==="
echo "IMPORTANT: SSH in and edit /home/ubuntu/yt-scripter/.env with your Anthropic API key"
echo "Then run: sudo systemctl restart yt-scripter"
