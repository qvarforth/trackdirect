FROM nginx:latest
COPY config/reverseproxy-default.conf /etc/nginx/conf.d/default.conf
