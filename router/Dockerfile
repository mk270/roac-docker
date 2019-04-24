FROM nginx

RUN mkdir -p /etc/nginx/tls
COPY tls/* /etc/nginx/tls/

COPY default.conf /etc/nginx/conf.d/default.conf

