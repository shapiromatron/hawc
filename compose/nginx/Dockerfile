# Requires a path to nginx configuration, for example:
#
# export configuration_file=./compose/nginx/nginx.conf && docker-compose build nginx
# export configuration_file=./data/nginx.conf && docker-compose build nginx

FROM nginx:1.11.12-alpine

ARG configuration_file

ADD ./data/ssl /etc/nginx/ssl
ADD $configuration_file /etc/nginx/nginx.conf
