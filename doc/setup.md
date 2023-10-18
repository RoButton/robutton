

# Raspberry Pi: Setup


## Generell
- `sudo -i`für root konsole `exit` to leave
- `sudo raspi-config` für raspberry konfiguration anpassungen

### Vorbereitungen

- Raspbian OS auf SD-Karte laden (e.g. balena etcher)
- Raspberry Konfiguration: Tastatur Layout, Hostname ändern, SSH aktivieren, Boot to Desktop deaktivieren, Pi autologin deaktivieren -> Reboot


### Raspberry Benutzer Ändern

- cmd: `groups` gibt eine Liste von Benutzergruppen

- neuen Benutzer thomas erstellen, verwende die Benutzergruppen von vorher:
`sudo useradd -m -G adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,gpio,i2c,spi thomas`

- `sudo passwd thomas` zum setzen eines neuen passworts

- `sudo shutdown -h now` -> dann pi stromkabel neu einstecken und als neuer user thomas einloggen

- `sudo deluser --remove-all-files pi` user pi entfernen

### Raspberry Pi Allgemein

- Packages auf den neuesten Stand bringen: `sudo apt-get update` dann `sudo apt-get upgrade`
- - evtl `sudo apt-get upgrade --fix-missing` bei fehler
- Notwendig für Keyring: `sudo apt-get install build-essential libssl-dev libffi-dev python-dev`
- Erlaubt dass Bluetooth Scanning möglich ist ohne sudo: `sudo setcap cap_net_raw+ep /usr/bin/hcitool`

### Nginx Installieren

- `sudo apt-get install nginx` erstellt ordner `/var/www/html/`
- `sudo systemctl status nginx` um den status von Nginx abzufragen
- `sudo nano /etc/nginx/sites-available/switchbot`
um die folgende Konfigurations Datei zu erstellen und verwenden:

```
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
```

- Default Konfiguration löschen und unsere Datei als default einstellen:
`sudo rm /etc/nginx/sites-enabled/default`
`sudo ln -s /etc/nginx/sites-available/switchbot /etc/nginx/sites-enabled`


#### HTTPS (Zertifikate) einrichten

- SSL Konfigurationsdatei erstellen `nano switchbot.conf`

```
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
```

- SSL Zertifikat erstellen anhand Konfigurationsdatei:
`sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/pi-switchbot.key -out /etc/ssl/certs/pi-switchbot.crt -config switchbot.conf`
(Kann über Browser heruntergeladen werden)

- Eigene Diffie Helmann Parameter erstellen (geht lange)
- `sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048`

### Github Aufsetzen
- Clone Repository in Ordner: `sudo -i` für in root konsole zu kommen, dann `cd /var/www/html/`,  dann `git clone https://github.com/nicolas-kuechler/switchbot.git`
- Owner vom Code Ordner ändern `sudo chown -R thomas switchbot`

### Python Environment Aufsetzen

- run `pip install pipenv`
- add `PATH=~/.local/bin:$PATH` to `~/.bashrc` and reload it with `source ~/.bashrc`
- in ordner `/var/www/html/switchbot/src`  `pipenv install -r ./../requirements.txt`


### Gunicorn aufsetzen

- Konfigurationsdatei erstellen: `sudo nano /etc/systemd/system/gunicorn.service`

```
[Unit]
Description=gunicorn daemon for /var/www/html/switchbot/src/main.py
After=network.target

[Service]
User=thomas
Group=thomas
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/html/switchbot/src/
ExecStart=/home/thomas/.local/bin/pipenv run gunicorn --bind=unix:/tmp/gunicorn.sock --workers=1 main:app --timeout 80 --access-logfile /var/www/html/log/gunicorn_access.log --error-logfile /var/www/html/log/gunicorn_error.log --log-file /var/www/html/log/gunicorn.log --log-level debug --capture-output
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

[Install]
WantedBy=multi-user.target
```
- Gunicorn Log Ordner erstellen: `sudo mkdir /var/www/html/log/`
- Gunicorn Log Ordner Berechtigung anpassen: `sudo chown -R thomas log`
- Gunicorn aktivieren: `sudo systemctl enable gunicorn`
- Gunicorn starten: `sudo systemctl start gunicorn`
- Gunicorn status: `sudo systemctl status gunicorn`
- Gunicorn neustarten (z.B. notwendig nach Login Passwort Änderung) `sudo systemctl restart gunicorn`
- `systemctl daemon-reload`


### Konfiguration Switchbot Applikation
- DB Pfad anpassen: `configmodule.py` öffnen und `DB_PATH` auf z.B. `/var/www/html/switchbot/db.json` ändern
- Token Expiration Time setzen: `configmodule.py` öffnen und `JWT_TOKEN_EXPIRE_HOURS` anpassen
- Login Passwort setzen: `python login_password.py` und dann Anweisungen folgen
- Passwörter werden mittels keyring verschlüsselt abgelegt unter: `~/.local/share/python_keyring/keyring_pass.cfg`


### Keyring Configuration
- Keyring Deaktivieren: In `~/.local/share/python_keyring/keyringc.cfg`:

```
[backend]
default-keyring=keyrings.alt.file.PlaintextKeyring
```
