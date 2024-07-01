Create .env file
```
BOT_TOKEN=token
ADMIN_CHAT_ID=adminid
TIMEOUT=15
TURN_ON_NOTIFY=True
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
ExecStartPre=/bin/sleep 1
ExecStart=/opt/e-energy/venv/bin/python /opt/e-energy/bot.py
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
systemctl start energybot.service`
```



Run worker.py to process notification  and sync.py to sync inforamtion about energy

crontab -e
```
*/30**** /opt/e-energy/venv/bin/python /opt/e-energy/bot.py # e-energy sync service
*/15**** /opt/e-energy/venv/bin/python  /opt/e-energy/bot.py # e-energy worker service
```
