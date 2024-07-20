Create .env file
```
BOT_TOKEN=token
ADMIN_CHAT_ID=adminid
TIMEOUT=15
TURN_ON_NOTIFY=True
ENERGY_BASE_URL=
```

Run bot.py as service for pooling
Loggin as root to the VM:
  `systemctl edit --force --full energybot.service`

create this unit:
```
[Unit]
Description=E-Energy Bot Service
Wants=network.target
After=network.target

[Service]
WorkingDirectory=/opt/e-energy
ExecStartPre=/bin/sleep 1
ExecStart=/opt/e-energy/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target

```
Eneable service:
`systemctl enable energybot.service`
Check status:
`systemctl status energybot.service`
Start if needed:

```
systemctl start energybot.service
```

Run worker.py to process notification and sync.py to sync information about energy schedule. Schedule it using cron: `crontab -e`
```
*/30 * * * * cd /opt/e-energy/ && venv/bin/python sync.py # e-energy sync service
*/15 * * * * cd /opt/e-energy/ && venv/bin/python worker.py # e-energy worker service
```
