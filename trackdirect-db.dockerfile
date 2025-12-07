FROM postgres:17
COPY misc/database/tables/* /docker-entrypoint-initdb.d/
COPY config/postgresql.conf /etc/postgresql.conf
RUN chown :999 /etc/postgresql.conf
RUN chmod 770 /etc/postgresql.conf
RUN chmod g+s /etc/postgresql.conf
VOLUME /var/lib/postgresql/data
