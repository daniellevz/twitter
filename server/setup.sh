#! /bin/sh
docker stop mq
docker rm mq
docker run -d --hostname mq --name mq -p 5672:5672 rabbitmq:3
