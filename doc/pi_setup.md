
# Raspberry Pi: Setup


- create ssh-key for github

- install miniconda:
  ```wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh```

  ```sh Miniconda2-latest-Linux-x86_64.sh```

  ```source .bashrc``` 



wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
sudo bash ./Miniconda3-latest-Linux-armv7l.sh -> change dir to /home/pi/miniconda3
nano /home/pi/.bashrc -> add line: export PATH="/home/pi/miniconda3/bin:$PATH"
source .bashrc  -> to avoid restart

conda -h  -> to check 
conda config --add channels rpi  -> for python 3.6 install
sudo chown -R pi miniconda3  -> change owner of folder 
conda install python=3.6 
conda create -n hc python=3.6

source activate hc -> to activate conda env

sudo apt-get install build-essential libssl-dev libffi-dev python-dev     -> before install keyring
sudo setcap cap_net_raw+ep /usr/bin/hcitool    -> allows to run scanning without sudo python 



## NGinx 

sudo apt-get update && sudo apt-get upgrade
sudo apt-get install nginx

 cd /var/www/html/
  sudo systemctl status nginx
   cd /etc/nginx/sites-available/
sudo touch switchbot
sudo nano switchbot ->

```
server {
	listen 80 default_server;
	listen [::]:80;

	root /var/www/html;

	server_name example.com;

	location /static {
	    alias /var/www/html/static;
	}

	location / {
	    try_files $uri @wsgi;
	}

	location @wsgi {
	    proxy_pass http://unix:/tmp/gunicorn.sock;
	    include proxy_params;
	}

	location ~* .(ogg|ogv|svg|svgz|eot|otf|woff|mp4|ttf|css|rss|atom|js|jpg|jpeg|gif|png|ico|zip|tgz|gz|rar|bz2|doc|xls|exe|ppt|tar|mid|midi|wav|bmp|rtf)$ {
	    access_log off;
	    log_not_found off;
	    expires max;
	}
}

```

 cd /etc/nginx/sites-enabled/
  sudo rm default
  sudo ln -s /etc/nginx/sites-available/switchbot .
 sudo nginx -t
 sudo service nginx reload



 sudo cp -avr ~/Dev/switchbot /var/www/html          -> move switchbot code in server folder

 sudo chown -R $USER /var/www/html/switchbot         -> change ownership of folder


sudo nano /etc/systemd/system/gunicorn.service

```
[Unit]
Description=gunicorn daemon for /var/www/html/switchbot/src/app.py
After=network.target

[Service]
User=pi
Group=pi
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/html/switchbot/src/
ExecStart=/home/pi/miniconda3/envs/hc/bin/gunicorn --bind=unix:/tmp/gunicorn.sock --workers=4 app:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

[Install]
WantedBy=multi-user.target

```


sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn



systemctl daemon-reload
sudo systemctl restart gunicorn    -> to restart gunicorn (e.g.)


## HTTPS


sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/pi-switchbot.key -out /etc/ssl/certs/pi-switchbot.crt -config switchbot.conf


""" -> switchbot.conf

[req]
default_bits       = 2048
distinguished_name = req_distinguished_name
x509_extensions    = v3_ca
prompt             = no

[req_distinguished_name]
C  = CH
ST = Schwyz
L  = Seewen
O  = Kuechler
CN = switchbots.dynu.net

[v3_ca]
subjectAltName = @alt_names

[alt_names]
DNS.1  = switchbots.dynu.net
DNS.2  = www.switchbots.dynu.net
DNS.3  = raspberrpi-dg.lan
DNS.4  = 192.168.42.51



"""

sudo openssl dhparam 2048 -out /etc/ssl/certs/dhparam.pem


"""
server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;

        server_name switchbots.dynu.net www.switchbots.dynu.net;
        root /var/www/html;

        ssl_certificate     /etc/ssl/certs/pi-switchbot.crt;
        ssl_certificate_key /etc/ssl/private/pi-switchbot.key;
        ssl_protocols TLSv1.2;
        ssl_ciphers "EECDH+ECDSA+AESGCM EECDH+aRSA+AESGCM EECDH+ECDSA+SHA384 EECDH+ECDSA+SHA256 EECDH+aRSA+SHA384 EECDH+aRSA+SHA256 EECDH+aRSA+RC4 EECDH EDH+aRSA HIGH !RC4 !aNULL !eNULL !LOW !3DES !MD5 !EXP !PSK !SRP !DSS";
        ssl_dhparam /etc/ssl/certs/dhparam.pem;

        location / {
            try_files $uri @wsgi;
        }

        location @wsgi {
            proxy_pass http://unix:/tmp/gunicorn.sock;
            include proxy_params;
        }
}

server {
    listen 80;
    server_name switchbots.dynu.net www.switchbots.dynu.net;
    return 301  https://switchbots.dynu.net:8995$request_uri;
}



"""



## Bluetooth


## Static IP

Open the dhcpcd file and add the static ip address.

```sudo nano /etc/dhcpcd.conf```

```
interface eth0
static ip_address=192.168.42.139/24

interface wlan0
static ip_address=192.168.42.139/24
```

https://thepihut.com/blogs/raspberry-pi-tutorials/how-to-give-your-raspberry-pi-a-static-ip-address-update