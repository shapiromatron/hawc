FROM postgres:18-alpine

RUN apk update && \
    apk upgrade --available && \
    rm -rf /var/cache/apk/*

# add backup scripts
ADD backup.sh /usr/local/bin/backup
ADD restore.sh /usr/local/bin/restore
ADD list-backups.sh /usr/local/bin/list-backups
