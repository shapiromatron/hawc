FROM nginx:alpine-slim

RUN apk update && \
    apk upgrade --available && \
    rm -rf /var/cache/apk/*

COPY ./wait-for.sh /wait-for.sh
