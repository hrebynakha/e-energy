sudo apt install -y build-essential python3-dev libxml2-dev libxslt1-dev
pip install -r requirements.txt 
cp .env.example .env
python main.py --run makemigrations
python main.py --run migrate
python main.py --run collectstatic



sudo apt install nginx
pip install gunicorn

cp conf/gunicorn.socket /etc/systemd/system/gunicorn.socket
cp conf/gunicorn.service /etc/systemd/system/gunicorn.service
cp conf/energybot.service /etc/systemd/system/energybot.service

sudo systemctl daemon-reload

cp conf/nginx.conf /etc/nginx/conf.d/e-energy.conf 

IP=$(hostname -I | awk '{print $1}')
sudo sed -i "s/server_domain_or_IP/$IP/g" /etc/nginx/conf.d/e-energy.conf


sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

echo "Starting nginx and gunicorn services ..."

sudo nginx -t
sudo systemctl restart nginx
sudo systemctl restart gunicorn.socket
sudo systemctl restart gunicorn.service

echo "Adding cron jobs ..."

LINE1="*/30 * * * * /opt/e-energy/venv/bin/python /opt/e-energy/main.py --run sync # e-energy sync service"
LINE2="*/15 * * * * /opt/e-energy/venv/bin/python /opt/e-energy/main.py --run worker # e-energy worker service"

(crontab -l 2>/dev/null; echo "$LINE1"; echo "$LINE2") | crontab -



echo "Installation completed successfully!"


echo "Trigger sync service ..."
main.py --run sync


echo "Trigger worker service ..."
main.py --run worker



python energybot/web/manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = "admin"
password = "admin"
email = "admin@example.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email=email)
    print("Superuser created!")
else:
    print("Superuser already exists.")
EOF
echo "Superuser created..."


echo "WARNING: Edit the .env file to configure bot token and admin chat id and re-run workers (or wait for cron jobs)"
echo "WARNING: This project is in development mode and not ready for production use"
echo "Please use it at your own risk"
echo "Go to http://$IP to see the result.Admin: admin/admin"
