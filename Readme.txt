python app.py --ngrok

TEST IF BLOCKED
cd C:\Users\hands\Documents\Claude\yt-scripter
python -c "from core.transcript import get_transcript; t = get_transcript('dQw4w9WgXcQ'); print('UNBLOCKED' if t else 'STILL BLOCKED')"


3.20.182.43



The server is running. Gunicorn is up with 2 workers, nginx is proxying. The only remaining step is setting your Anthropic API key.

You need to SSH in and set it. Run this in PowerShell:

ssh -i C:\Users\hands\.ssh\lightsail-key.pem ubuntu@3.20.182.43

Or I can set it for you if you paste your API key here (it won't be stored anywhere permanent). Alternatively, run this one-liner replacing YOUR_KEY:

ssh -i /tmp/lightsail-key.pem ubuntu@3.20.182.43 "echo 'ANTHROPIC_API_KEY=YOUR_KEY' > /home/ubuntu/yt-scripter/.env && sudo systemctl restart yt-scripter"

Once the key is set, visit http://3.20.182.43 in your browser — that's your live YT Scripter!


Updated project setup tasks for yt-scripter application
Updated project setup tasks for yt-scripter application

★ Insight ─────────────────────────────────────

164MB memory usage out of 512MB — comfortably under the limit. Gunicorn's 2 workers + nginx leave ~300MB free for Python to process requests.
Static IP (3.20.182.43) is free as long as it's attached to a running instance. If you stop the instance, the static IP starts costing ~$0.005/hr to prevent IP squatting.
To update the app in the future: push to GitHub, then SSH in and run bash /home/ubuntu/yt-scripter/deploy/update.sh.


For the Lightsail server, add the same vars when you SSH in:

ssh -i /tmp/lightsail-key.pem ubuntu@3.20.182.43 "cat >> /home/ubuntu/yt-scripter/.env << 'EOF'
WEBSHARE_PROXY_USER=okquntcg
WEBSHARE_PROXY_PASS=nqhce218h7ln
EOF
sudo systemctl restart yt-scripter"


Everything's deployed. For future updates, just run:

cd C:\Users\hands\Documents\Claude\yt-scripter
git add -A && git commit -m "description" && git push
ssh -i /tmp/lightsail-key.pem ubuntu@3.20.182.43 "cd /home/ubuntu/yt-scripter && bash deploy/update.sh"