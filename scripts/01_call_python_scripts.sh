#!/bin/sh
################################################################################
# Revised to add in the necessary scripts to create a lambda and its IAM
# permissions when the local stack begins when the docker containers build.

# Interestingly, the event-source mapping added to the lambda requires the ARN
# of the event source - the SQS. However, at the point this lambda is created,
# no corresponding SQS has been created yet. This probably succeeds because
# localstack is looking for a placeholder value at instantiation and all ARNs
# follow a general patterns (as ARNs do) but there's no validation since we're
# only mocking resources
################################################################################


echo "downloding localstack dependency"
pip install localstack-client

echo  "starting scripts"
python /tmp/scripts/create_iam.py
chmod +x /tmp/scripts/setup-lambda.sh
sh /tmp/scripts/setup-lambda.sh
python /tmp/scripts/create_and_write_to_queue.py

echo "winding down"
