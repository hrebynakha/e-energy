sudo apt install -y build-essential python3-dev libxml2-dev libxslt1-dev
pip install -r requirements.txt 
cp .env.example .env
python main.py --run makemigrations
python main.py --run migrate



sudo apt install nginx

cp conf/gunicorn.socket /etc/systemd/system/gunicorn.socket
cp conf/gunicorn.service /etc/systemd/system/gunicorn.service
cp conf/energybot.service /etc/systemd/system/energybot.service

sudo systemctl daemon-reload

cp conf/nginx.conf /etc/nginx/conf.d/e-energy.conf 

IP=$(hostname -I | awk '{print $1}')
sudo sed -i "s/server_domain_or_IP/$IP/g" /etc/nginx/conf.d/e-energy.conf


sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket



sudo nginx -t
sudo systemctl restart nginx

echo "Installation completed successfully!"
echo "Got to http://$IP to see the result"