FROM nginx:1.17.10-alpine

COPY ./wait-for.sh /wait-for.sh
COPY ./entrypoint.sh /entrypoint.sh
ADD ./conf/nginx.conf /etc/nginx/nginx.conf
ADD ./static /etc/nginx/nginx.conf

ENTRYPOINT ["/entrypoint.sh"]
