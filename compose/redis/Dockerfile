# https://github.com/docker-library/redis/blob/master/6.0/alpine/Dockerfile
# https://github.com/redis-io/redis/blob/6.0/redis.conf
# https://github.com/docker-library/redis/issues/46#issuecomment-211599210
FROM redis:6-alpine

ENV REDIS_PASSWORD default-password
CMD ["sh", "-c", "exec redis-server --requirepass \"$REDIS_PASSWORD\""]
