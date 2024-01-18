FROM postgres:12-alpine

RUN apk update && \
    apk upgrade --available && \
    rm -rf /var/cache/apk/*

# add backup scripts
ADD backup.sh /usr/local/bin/backup
ADD restore.sh /usr/local/bin/restore
ADD list-backups.sh /usr/local/bin/list-backups

# add custom entrypoint
ADD docker-entrypoint.sh /docker-entrypoint-2.sh

ENTRYPOINT ["docker-entrypoint-2.sh"]
