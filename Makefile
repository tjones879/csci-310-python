
deploy: docker-compose.yml Dockerfile
	sudo docker-compose -f docker-compose.yml up -d --build
destroy: docker-compose.yml
	sudo docker-compose -f docker-compose.yml down
deploydev: docker-compose-dev.yml Dockerfile
	sudo docker-compose -f docker-compose-dev.yml up -d --build
destroydev: docker-compose-dev.yml
	sudo docker-compose -f docker-compose-dev.yml down
restart:
	sudo docker restart multipong-web multipong-loop
clearredis:
	sudo docker restart multipong_redis_1
