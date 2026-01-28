# https://hub.docker.com/hardened-images/catalog/dhi/postgres/images/
FROM dhi.io/postgres:16-alpine3.22

# add backup scripts
ADD backup.sh /usr/local/bin/backup
ADD restore.sh /usr/local/bin/restore
ADD list-backups.sh /usr/local/bin/list-backups
