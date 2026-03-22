#!/bin/bash
# Pull latest code and restart the service
set -euo pipefail

cd /home/ubuntu/yt-scripter
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart yt-scripter

echo "Updated and restarted."
