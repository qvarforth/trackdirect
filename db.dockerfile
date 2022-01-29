FROM postgres
COPY misc/database/tables/* /docker-entrypoint-initdb.d/
