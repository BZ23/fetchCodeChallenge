#!/bin/sh
################################################################################
# Quick script to pull lambda log sample from localstack cloudwatch logs
# variable values for:
# - lambda name
# - log stream list position provided
# - docker container name
################################################################################

lambdaName=fetch_lambda
echo "Variable - Lambda name: $lambdaName"

streamPos=6
echo "Variable - Will pull position from log stream list: $streamPos"

dockerContainerName=fetchcodechallenge_localstack_1
echo "Variable - Docker container name used to find Container ID: $dockerContainerName"

containerID=`docker ps -aqf "name=$dockerContainerName"`
echo "ContainerID: $containerID"

logStreamName=`docker exec $containerID awslocal logs describe-log-streams --log-group-name /aws/lambda/$lambdaName | jq -r '.logStreams'[$streamPos]'.logStreamName'`
echo "LogStreamName: $logStreamName"

docker exec $containerID awslocal logs get-log-events --log-group-name /aws/lambda/fetch_lambda --log-stream-name $logStreamName
