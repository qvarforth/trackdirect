# APRS Track Direct

APRS Track Direct is a collection of tools that can be used to run an APRS website. You can use data from APRS-IS, CWOP-IS, OGN or any other source that uses the APRS specification.

Tools included are an APRS data collector, a websocket server, a javascript library (websocket client and more) and a website example (which can of course be used as is).

## What is APRS?
APRS (Automatic Packet Reporting System) is a digital communications system that uses packet radio to send real time tactical information. The APRS network is used by ham radio operators all over the world.

Information shared over the APRS network is for example coordinates, altitude, speed, heading, text messages, alerts, announcements, bulletins and weather data.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes (but they are of course also valid for you who want to set up a public website).

Please note that the instructions is not intended to be something that you can follow exactly without any adaptions. See the instructions as initial tips on how the tools can be used, and read the code to get a deeper understanding.

Further down you will find some information how to install trackdirect with Docker and Docker Compose.

### Prerequisites

What things you need to install and how to install them. These instructions are for Ubuntu 20.04

Install some ubuntu packages
```
sudo apt update
sudo apt-get install libpq-dev postgresql-12 postgresql-client-common postgresql-client libevent-dev apache2 php libapache2-mod-php php-dom php-pgsql libmagickwand-dev imagemagick php-imagick inkscape php-gd libjpeg-dev python3 python3-dev python3-pip python-is-python3
```

### Set up aprsc
You should not to connect your collector and websocket server directly to a public APRS server (APRS-IS, CWOP-IS or OGN server). The collector will use a full feed connection and each websocket client will use a filtered feed connection (through the websocket server). To not cause extra load on public servers it is better to run your own aprsc server and let your collector and all websocket connections connect to that instead (will result in only one full feed connection to a public APRS server).

Note that it seems like aprsc needs to run on a server with a public ip, otherwise uplink won't work.

#### Installation
Follow the instructions found [here](http://he.fi/aprsc/INSTALLING.html).

#### Config file
You must modify the configuration file before starting aprsc.
```
sudo vi /opt/aprsc/etc/aprsc.conf
```

Uplink examples:
```
# Uplink "APRS-IS" ro tcp rotate.aprs.net 10152
# Uplink "CWOP" ro tcp cwop.aprs.net 10152
# Uplink "OGN" ro tcp aprs.glidernet.org 10152
```
Only use one of them, if you are going to use multiple sources you should set up muliple aprsc servers and run multiple collectors. That will enable you to have different settings for different sources.

#### Start aprsc server
Start aprsc
```
sudo systemctl start aprsc
```

If you run multiple aprsc instances you need to select different data och log directories (and of course different tcp ports in configuration file). Running multiple aprsc instances is only needed if you fetch data from multiple sources (like both APRS-IS and CWOP-IS).

Should be possible to start multiple aprsc instances by using something like this:
```
sudo /opt/aprsc/sbin/aprsc -u aprsc -t /opt/aprsc -c /etc/aprsc.conf -r /logs -o file -f
sudo /opt/aprsc/sbin/aprsc -u aprsc -t /opt/aprsc2 -c /etc/aprsc2.conf -r /logs2 -o file -f
```

### Installing Track Direct

Note: TrackDirect have to be installed in the user home directory, it can't be in any subdirectory.


Start by cloning the repository
```
git clone https://github.com/qvarforth/trackdirect
cd trackdirect
```

Before installing all python requirements it is likly that you need to upgrade pyOpenSSL.
```
sudo python -m easy_install --upgrade pyOpenSSL
```

Install needed python libs
```
pip install -r requirements.txt
```

#### Set up database

Set up the database (connect to database using: "sudo -u postgres psql"). You need to replace "my_username".  Note that APRS using UTF-8 encoding so it may be necessary to specify as shown.
```
CREATE DATABASE trackdirect ENCODING 'UTF8';

CREATE USER my_username WITH PASSWORD 'foobar';
ALTER ROLE my_username WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE "trackdirect" to my_username;
```

Might be good to add password to password-file:
```
vi ~/.pgpass
```

##### Increase database performance
It might be a good idea to play around with some Postgresql settings to improve performance (for this application, speed is more important than minimizing the risk of data loss).

Some settings in /etc/postgresql/12/main/postgresql.conf that might improve performance:
```
shared_buffers = 2048MB              # I recommend 25% of total RAM
synchronous_commit=off               # Avoid writing to disk for every commit
commit_delay=100000                  # Will result in a 0.1s commit delay
```

Restart postgresql
```
sudo /etc/init.d/postgresql restart
```

##### Set up database tables
The script should be executed by the user that owns the database "trackdirect".
```
~/trackdirect/server/scripts/db_setup.sh trackdirect 5432 ~/trackdirect/misc/database/tables/
```

#### Set up OGN device data
If you are using data from OGN (Open Glider Network) it is IMPORTANT to keep the OGN data updated (the database table ogn_devices). This is important since otherwise you might show airplanes that you are not allowed to show. I recommend that you run this script at least once every hour (or more often). The script should be executed by the user that you granted access to the database "trackdirect".
```
~/trackdirect/server/scripts/ogn_devices_install.sh trackdirect 5432
```

#### Configure trackdirect
Before starting the websocket server you need to update the trackdirect configuration file (trackdirect/config/trackdirect.ini). Read through the configuration file and make any necessary changes.
```
vi ~/trackdirect/config/trackdirect.ini
```

#### Start the collectors
Before starting the collector you need to update the trackdirect configuration file (trackdirect/config/trackdirect.ini).

Start the collector by using the provided shell-script. Note that if you have configured multiple collectors (fetching from multiple aprs servers, for example both APRS-IS and CWOP-IS) you need to call the shell-script multiple times. The script should be executed by the user that you granted access to the database "trackdirect".
```
~/trackdirect/server/scripts/collector.sh trackdirect.ini 0
```

#### Start the websocket server
When the user interacts with the map we want it to be populated with objects from the backend. To achive good performance we avoid using background HTTP requests (also called AJAX requests), instead we use websocket communication. The included trackdirect js library (trackdirect.min.js) will connect to our websocket server and request objects for the current map view.

Start the websocket server by using the provided shell script, the script should be executed by the user that you granted access to the database "trackdirect".
```
~/trackdirect/server/scripts/wsserver.sh trackdirect.ini
```

If you have enabled a firewall, make sure the selected port is open (we are using port 9000 by default, can be changed in trackdirect.ini).
```
sudo ufw allow 9000
```

#### Trackdirect js library
All the map view magic is handled by the trackdirect js library, it contains functionality for rendering the map (using Google Maps API or Leaflet), functionality used to communicate with backend websocket server and much more.

If you do changes in the js library (jslib directory) you need to execute build.sh to deploy the changes to the htdocs directory.

```
~/trackdirect/jslib/build.sh
```

#### Adapt the website (htdocs)
For setting up a copy on your local machine for development and testing purposes you do not need to do anything, but for any other pupose I really recommend you to adapt the UI.

First thing to do is probably to select which map provider to use, look for stuff related to map provider in "index.php". Note that the map providers used in the demo website may not be suitable if you plan to have a public website (read their terms of use).

If you make no changes, at least add contact information to yourself, I do not want to receive questions regarding your website.


#### Set up webserver
Webserver should already be up and running (if you installed all specified ubuntu packages).

Add the following to /etc/apache2/sites-enabled/000-default.conf. You need to replace "my_username".
```
<Directory "/home/my_username/trackdirect/htdocs">
    Options SymLinksIfOwnerMatch
    AllowOverride All
    Require all granted
</Directory>
```

Change the VirtualHost DocumentRoot: (in /etc/apache2/sites-enabled/000-default.conf):
```
DocumentRoot /home/my_username/trackdirect/htdocs
```

Enable rewrite and restart apache
```
sudo a2enmod rewrite
sudo systemctl restart apache2
```

For the symbols and heatmap caches to work we need to make sure the webserver has write access (the following permission may be a little bit too generous...)
```
chmod 777 ~/trackdirect/htdocs/public/symbols
chmod 777 ~/trackdirect/htdocs/public/heatmaps
```

If you have enabled a firewall, make sure port 80 is open.
```
sudo ufw allow 80
```

## Deployment

If you want to set up a public website you should install a firewall and setup SSL certificates. For an easy solution I would use ufw to handle iptables, Nginx as a reverse proxy and use let’s encrypt for SSL certificates.

### Schedule things using cron
If you do not have infinite storage we recommend that you delete old packets, schedule the remover.sh script to be executed about once every hour. And again, if you are using OGN as data source you need to run the ogn_devices_install.sh script at least once every hour.

Note that the collector and wsserver shell scripts can be scheduled to start once every minute (nothing will happen if it is already running). I even recommend doing this as the collector and websocket server are built to shut down if something serious goes wrong (eg lost connection to database).

Crontab example (crontab for the user that owns the "trackdirect" database)
```
40 * * * * ~/trackdirect/server/scripts/remover.sh trackdirect.ini 2>&1 &
0 * * * * ~/trackdirect/server/scripts/ogn_devices_install.sh trackdirect 5432 2>&1 &
* * * * * ~/trackdirect/server/scripts/wsserver.sh trackdirect.ini 2>&1 &
* * * * * ~/trackdirect/server/scripts/collector.sh trackdirect.ini 0 2>&1 &
```

### Server Requirements
How powerful server you need depends on what type of data source you are going to use. If you, for example, receive data from the APRS-IS network, you will probably need at least a server with 4 CPUs and 8 GB of RAM, but I recommend using a server with 8 CPUs and 16 GB of RAM.


## Getting Started - Docker
Everything is prepared to run trackdirect inside of docker containers. As there is a Docker Compose file the setup is very simple and fast.

### Install Docker and the Docker Compose plugin
Install [Docker and docker-compose-plugin](https://docs.docker.com/engine/install/) as per instructions on their website.

### Config file
Adopt the config in `config/aprsc.conf` and `config/trackdirect.ini`. In `trackdirect.ini` additionally search for 'docker' and change the lines as described in the comments.


### Run Docker Compose for development containers
To startup trackdirect in a development container run this Docker Compose command:

```
docker compose up
```

If you want to run the container in daemon mode (background) add `-d` to the command and use `docker compose logs -f` to watch the output on demand. To stop the containers use `docker compose down`.

### Run Docker Compose for the latest published docker images

@peterus is creating regular docker images from this repository. With the release Docker Compose file you don't need to install and compile everything on your own.

```
docker compose -f docker-compose-rel.yml up
```
This command also accepts `-d` to run as a daemon.

## Contribution
Contributions are welcome. Create a fork and make a pull request. Thank you!

## Disclaimer
These software tools are provided "as is" and "with all it's faults". We do not make any commitments or guarantees of any kind regarding security, suitability, errors or other harmful components of this source code. You are solely responsible for ensuring that data collected and published using these tools complies with all data protection regulations. You are also solely responsible for the protection of your equipment and the backup of your data, and we will not be liable for any damages that you may suffer in connection with the use, modification or distribution of these software tools.
