# Manual installation for Debian (10/11/12) \Ubuntu (16.04/18.04/20.04)
## - Update packages
      apt update
## - Install postgres and required packages
      apt install postgresql-16 postgresql-client-common postgresql-client
## - Install other required packages
      apt install sudo git libpq-dev libevent-dev libmagickwand-dev imagemagick inkscape
## - Install python3 and required packages
      apt install python3 python3-dev python3-pip python-is-python3 python3-full
      apt install python3-psycopg2 python3-setuptools python3-autobahn python3-twisted python3-jsmin python3-psutil 
      cd /opt
      git clone https://salsa.debian.org/python-team/packages/pympler.git    
      cd pympler
      python3 setup.py install
## - Install php and required packages
      apt install php libapache2-mod-php php-dom php-pgsql php-imagick php-dev php-pear php-gd
## - Install pythons aprs library
      cd /opt    
      git clone https://github.com/rossengeorgiev/aprs-python    
      cd aprs-python    
      python3 setup.py install
## - Install heatmap function from source
      cd /opt    
      wget http://jjguy.com/heatmap/heatmap-2.2.1.tar.gz    
      tar xzf heatmap-2.2.1.tar.gz    
      cd heatmap-2.2.1    
      python3 setup.py install
  
  ---error1---
  
  File "/opt/heatmap-2.2.1/setup.py", line 15
      print "On Windows, skipping build_ext."
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      
  SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
  
  --- To fix this error edit likne 15 of setup.py like this bellow ---
  
    print ("On Windows, skipping build_ext.")
  
  ---error2---
  
  /usr/lib/python3/dist-packages/setuptools/_distutils/dist.py:289: UserWarning: Unknown distribution option: 'test_suite'
    warnings.warn(msg)
    
  /usr/lib/python3/dist-packages/setuptools/_distutils/dist.py:289: UserWarning: Unknown distribution option: 'tests_require'
    warnings.warn(msg)
    
    File "/usr/local/lib/python3.13/dist-packages/heatmap/__init__.py", line 3
      except Exception, e:
      
             ^^^^^^^^^^^^
             
  SyntaxError: multiple exception types must be parenthesized
  
  --- To fix this error edit line 3 of __init__.py like this bellow: ---
  
    except Exception(e):
## - Server APRS
#### Install aprsc service from source
      cd /opt    
      git clone https://github.com/hessu/aprsc        
      cd /opt/aprsc/src        
       ./configure         
      make         
      make install        
      mkdir /usr/local/etc/aprsc        
      mkdir /usr/local/etc/aprsc/data        
      mkdir /usr/local/etc/aprsc/etc        
      mkdir /usr/local/etc/aprsc/logs        
      cp /opt/aprsc/sbin/* /usr/local/etc/aprsc        
      cp /opt/aprsc/etc/aprsc.conf /usr/local/etc/aprsc        
      cp /opt/aprsc/web -r /usr/local/etc/aprsc
#### Add a user for aprsc service
      adduser aprsc
    
    set shell nologin for user aprsc
#### Run aprsc service
      chown -R aprsc:aprsc /usr/local/etc/aprsc           
      sudo /usr/local/etc/aprsc/aprsc -u aprsc -t /usr/local/etc/aprsc -c aprsc.conf -r /logs -o file -f
## - Get trackdirect code
      cd /opt        
      git clone https://github.com/qvarforth/trackdirect
      cp /opt/trackdirect -r /root
#### Edit trackdirect.ini
      nano /root/trackdirect/config/trackdirect.ini
## - Setup db (create db, add user, set password and edit configs)
    sudo -u postgres psql
    CREATE DATABASE trackdirect;    
    GRANT ALL PRIVILEGES ON DATABASE trackdirect to postgres;    
    ALTER USER postgres PASSWORD 'foobar';
    \q
    
## - Settings for Postgres
#### Edit pg_hba.conf and add line bellow:
    host    all             all             127.0.0.1/32            md5
#### Edit postgresql.conf
    listen_addresses = 'localhost,192.168.0.1'
    
    shared_buffers = 2048MB              # I recommend 25% of total RAM
    synchronous_commit=off               # Avoid writing to disk for every commit    
    commit_delay=`100000`                # Will result in a 0.1s commit delay
#### Restart postgresql
     sudo service postgresql restart
#### Setup a tables of database
     cd /root/trackdirect/server/scripts
  
     sudo -u postgres ./db_setup.sh trackdirect 5432 /root/trackdirect/misc/database/tables/
## - Settings for Apache
#### Make directoryes for apache
          mkdir /var/www/trackdirect
          mkdir /var/www/trackdirect/config 
          cp /root/trackdirect/htdocs -r /var/www/trackdirect
          cp /root/trackdirect/config/trackdirect.ini /var/www/trackdirect/config
        
          chmod 777 /var/www/trackdirect/htdocs/public/symbols        
          chmod 777 /var/www/trackdirect/htdocs/public/heatmaps
#### Edit 000-default.conf
          <VirtualHost *:80>
             ServerAdmin webmaster@localhost
             DocumentRoot /var/www/trackdirect/htdosc/public
             ErrorLog ${APACHE_LOG_DIR}/aprs-error.log
             CustomLog ${APACHE_LOG_DIR}/aprs-access.log combined
                  <Directory "/var/www/trackdirect/htdosc/public">
                          Options  Indexes MultiViews SymLinksIfOwnerMatch
                          AllowOverride All
                          Require all granted
                  </Directory>
          </VirtualHost>
#### Restart Apache
          chown -R www-data:www-data /var/www
          sudo a2enmod rewrite
          sudo service apache2 restart
## - Edit crontab to start trackdirect service

      * * * * * ~/trackdirect/server/scripts/wsserver.sh trackdirect.ini 2>&1 &
      * * * * * ~/trackdirect/server/scripts/collector.sh trackdirect.ini 0 2>&1 &
      30 * * * * ~/trackdirect/server/scripts/remover.sh trackdirect.ini 2>&1 &
      0 * * * * ~/trackdirect/server/scripts/ogn_devices_install.sh trackdirect 5432 2>&1 &
          
