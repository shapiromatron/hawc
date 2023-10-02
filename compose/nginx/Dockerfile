FROM nginx:stable-alpine

RUN apk update && \
    apk upgrade --available && \
    rm -rf /var/cache/apk/*

COPY ./wait-for.sh /wait-for.sh
