FROM postgres
COPY misc/database/tables/* /docker-entrypoint-initdb.d/
VOLUME /var/lib/postgresql/data
