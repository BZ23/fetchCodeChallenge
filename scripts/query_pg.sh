#!/bin/sh
################################################################################
# Quick script to connect to postgres database.
#
# After adjusting the docker-compose file, a user defined network was used to
# allow communication across containers. Although this should be done by default
# with docker compose, a check of the docker networks showed that the containers
# for postgres and localstack were not in the same network. In addition, user
# defined networks permit the service name for postgres to be referenced in
# place of 'localhost'
#
# variable values for:
# - docker container name
################################################################################

dockerContainerName=`echo data-engineering-take-home_postgres_1`
echo "Variable - Docker container name used to find Container ID: $dockerContainerName"

containerID=`docker ps -aqf "name=$dockerContainerName"`
echo "ContainerID: $containerID"

user=postgres
host=postgres
port=5432
db=postgres

docker exec -it $containerID psql -d $db -U $user  -p $port -h $host -W
