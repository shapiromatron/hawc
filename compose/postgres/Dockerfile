FROM postgres:12-alpine

RUN apk update && \
    apk upgrade --available && \
    rm -rf /var/cache/apk/*

# add backup scripts
ADD backup.sh /usr/local/bin/backup
ADD restore.sh /usr/local/bin/restore
ADD list-backups.sh /usr/local/bin/list-backups

# make them executable
RUN chmod +x /usr/local/bin/restore && \
    chmod +x /usr/local/bin/list-backups && \
    chmod +x /usr/local/bin/backup
