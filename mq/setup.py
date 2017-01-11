docker stop mq
docker rm mq
docker run -d --hostname mq --name mq -p 5672:5672 rabbitmq:3
#docker run -d --hostname mq --name mq -e RABBITMQ_DEFAULT_USER=user -e RABITMQ_DEFAULT_PASSWORD=user -p 5672:5672 rabbitmq
#docker exec -it mq /bin/bash
