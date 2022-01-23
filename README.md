# APRS Track Direct

APRS Track Direct is a collection of tools that can be used to run an APRS website. You can use data from APRS-IS, CWOP-IS, OGN, HUBHAB, CBAPRS or any other source that uses the APRS specification.

Tools included are an APRS data collector, a websocket server, a javascript library (websocket client and more), a heatmap generator and a website example (which can of course be used as is).

Please note that it is almost 10 years since I wrote the majority of the code, and when the code was written, it was never intended to be published ...

## What is APRS?
APRS (Automatic Packet Reporting System) is a digital communications system that uses packet radio to send real time tactical information. The APRS network is used by ham radio operators all over the world.

Information shared over the APRS network is for example coordinates, altitude, speed, heading, text messages, alerts, announcements, bulletins and weather data.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes (but they are of course also valid for you who want to set up a public website).

### Prerequisites

What things you need to install and how to install them. These instructions are for Ubuntu 20.04

Install some ubuntu packages
```
sudo apt-get install libpq-dev postgresql-12 postgresql-client-common postgresql-client libevent-dev apache2 php libapache2-mod-php php-dom php-pgsql libmagickwand-dev imagemagick php-imagick inkscape
```

#### Install python
Unfortunately, the majority of this code was written when python 2 was still common and used, this means that the installation process needs to be adapted a bit. You might see some deprication warnings when starting the collector and websocket server.

Install python 2
```
sudo add-apt-repository universe
sudo apt update
sudo apt install python2 python2-dev
```

Install pip2 (pip for python 2)
```
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
```

Install needed python libs
```
pip2 install psycopg2-binary
pip2 install wheel
pip2 install setuptools
pip2 install autobahn[twisted]
pip2 install twisted
pip2 install pympler
pip2 install image_slicer
pip2 install jsmin
pip2 install psutil
```

Install the python aprs lib (aprs-python)
```
git clone https://github.com/rossengeorgiev/aprs-python
cd aprs-python/
pip2 install .
```

Install python library used for generating heatmap
```
wget http://jjguy.com/heatmap/heatmap-2.2.1.tar.gz
tar xzf heatmap-2.2.1.tar.gz
cd heatmap-2.2.1
sudo python2 setup.py install
```

### Installing

Start by cloning the repository
```
git clone https://github.com/qvarforth/trackdirect
```

#### Set up database

Set up the database (connect to database using: "sudo -u postgres psql")
```
CREATE DATABASE trackdirect;

CREATE USER {my_linux_username} WITH PASSWORD 'foobar';
ALTER ROLE {my_linux_username} WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE "trackdirect" to {my_linux_username};
```

Remember to add password to password-file:
```
vi ~/.pgpass
```

##### Increase performance
It might be a good idea to play around with some Postgresql settings to improve performance (for this application, speed is more important than minimizing the risk of data loss).

Some settings in /etc/postgresql/12/main/postgresql.conf that might improve performance:
```
shared_buffers = 2048MB              # I recommend 25% of total RAM
synchronous_commit=off               # Avoid writing to disk for every commit
commit_delay=100000                  # Will result in a 0.1s delay
```

Restart postgresql
```
sudo /etc/init.d/postgresql restart
```

##### Set up database tables
```
~/trackdirect/server/scripts/db_setup.sh trackdirect 5432 ~/trackdirect/misc/database/tables/
```

#### Set up OGN device data
If you are using data from OGN (Open Glider Network) it is IMPORTANT to keep the OGN data updated (the database table ogn_devices). This is important since otherwise you might show airplanes that you are not allowed to show. I recommend that you run this script at least once every hour (or more often).
```
~/trackdirect/server/scripts/ogn_devices_install.sh trackdirect 5432
```

#### Set up aprsc
You should not to connect to a public APRS server (APRS-IS, CWOP-IS or OGN server). The collector will use a full feed connection and each websocket client will use a filtered feed connection. To not cause extra load on public servers it is better to run your own aprsc server and let your collector and all websocket connections connect to that instead (will result in only one full feed connection to a public APRS server).

Note that it seems like aprsc needs to run on a server with a public ip, otherwise uplink won't work.

##### Download and install
```
wget http://he.fi/aprsc/down/aprsc-latest.tar.gz
tar xvfz aprsc-latest.tar.gz
cd aprsc-*/src
./configure
make
sudo make install
```

##### Create user
Create user to avoid running aprsc as root
```
sudo useradd -r -s /bin/false aprsc
sudo chown -R aprsc /opt/aprsc
sudo chgrp -R aprsc /opt/aprsc
```

##### Config file
You can find an example aprsc configuration file in the misc directory. Note that you need to modify the configuration file to make it work.
```
sudo cp ~/trackdirect/misc/aprsc.conf /opt/aprsc/etc/
```

##### Start aprsc server
Start the aprsc server using the configuration file that you selected. Note that if you run multiple aprsc instances you need to select different data och log directories (and of course different tcp ports in configuration file).
```
sudo /opt/aprsc/sbin/aprsc -u aprsc -t /opt/aprsc -c /etc/aprsc_aprs.conf -r /logs -o file -f
```

#### Start the collectors
Before starting the collector you need to update the trackdirect configuration file (trackdirect/config/trackdirect.ini).

Start the collector using the provided shell-script. Note that if you have configured multiple collectors (fetching from multiple aprs servers, for example both APRS-IS and CWOP-IS) you need to call the shell-script multiple times.
```
~/trackdirect/server/scripts/collector.sh trackdirect.ini 0
```

#### Start the websocket server
```
~/trackdirect/server/scripts/wsserver.sh trackdirect.ini
```

#### Start generating heatmaps
I recommend generating new heatmaps once every hour in production (I suggest that you schedule it using cron).

```
~/trackdirect/server/scripts/heatmapcreator.sh trackdirect.ini ~/trackdirect/htdocs/public/heatmaps
```

Generating heatmaps might take a while, look in log file to see the current status:
```
tail -f ~/trackdirect/server/log/heatmap.log
```

#### Javascript library (jslib)
If you do changes in the js library (jslib directory) you need to execute build.sh to deploy the changes to the htdocs directory.

```
~/trackdirect/jslib/build.sh
```

#### Adapt the website (htdocs)
For setting up a copy on your local machine for development and testing purposes you do not need to do anything, but for any other pupose I really recommend you to adapt the UI.

First thing to do is probably to add your map api keys, look for the string "&lt;insert map key here&gt;" in the file "index.php". Note that the map providers used in the demo website may not be suitable if you plan to have a public website (read their terms of use).

If you make no changes, at least add contact information to yourself, I do not want to receive questions regarding your website.


#### Set up webserver
Webserver should already be up and running (if you installed all specified ubuntu packages).

Let's redirect the html-directory to our htdocs/public directory (requires "Options FollowSymLinks" to be enabled).
```
cd /var/www
sudo mv html html_old
sudo ln -s /home/xyz/trackdirect/htdocs html
```

To enable the use of the .htaccess files you need to edit the file /etc/apache2/sites-enabled/000-default.conf (or whatever it is called in your system), and add "AllowOverride All".
```
<VirtualHost *:80>
    ...
    DocumentRoot /home/xyz/trackdirect/htdocs/public
    AllowOverride All
    ...
</VirtualHost>

```

Enable rewrite by running this command
```
sudo a2enmod rewrite
```

Restart apache
```
sudo systemctl restart apache2
```

For the symbols cache to work we need to make sure the webserver has write access to our htdocs/public/symbols directory (the following permission may be a little bit too generous...)
```
chmod 777 ~/trackdirect/htdocs/public/symbols
```

## Deployment

If you want to set up a public website you should install a firewall and setup SSL certificates. For an easy solution I would use ufw to handle iptables, Nginx as a reverse proxy and use let’s encrypt for SSL certificates.

### Stuff to start on boot
- apache2
- aprsc (see topic "Start aprsc server")
- collector (see topic "Start the collectors")
- wsserver (see topic "Start the websocket server")

Note that the collector and wsserver shell scripts can be scheduled to start once every minute (nothing will happen if it is already running). I even recommend doing this as the collector and websocket server are built to shut down if something serious goes wrong (eg lost connection to database).

### Schedule things using crontab
We recommend that your schedule the heatmapcreator shell script to be executed once every hour. If you do not have infinite storage we recommend that you delete old packets, schedule the remover.sh script to be executed at least once every day.

Use cron!

```
10 * * * * ~/trackdirect/server/scripts/heatmapcreator.sh trackdirect.ini ~/trackdirect/htdocs/public/heatmaps
40 1 * * * ~/trackdirect/server/scripts/remover.sh trackdirect.ini
```

And again, if you are using OGN as data source you need to run the ogn_devices_install.sh script at least once every hour
```
0 * * * * ~/trackdirect/server/scripts/ogn_devices_install.sh trackdirect 5432
```

### Server Requirements
How powerful server you need depends on what type of data source you are going to use. If you, for example, receive data from the APRS-IS network, you will probably need at least a server with 4 CPUs and 8 GB of RAM, but I recommend using a server with 8 CPUs and 16 GB of RAM.

## TODO
- Rewrite backend to use Python 3 instead of Python 2.
- Create a REST-API and replace the current website example with a new frontend written in Angular.

## Contribution
Contributions are welcome. Create a fork and make a pull request. Thank you!

## Disclaimer
This software is provided "as is" and "with all it's faults". We do not make any commitments or guarantees of any kind regarding security, suitability, errors or other harmful components of this software. You are solely responsible for ensuring that data collected and published using this software complies with all data protection regulations. You are also solely responsible for the protection of your equipment and the backup of your data, and we will not be liable for any damages that you may suffer in connection with the use, modification or distribution of this software.
