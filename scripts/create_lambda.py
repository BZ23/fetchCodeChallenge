"""Script to create the lambda used to consume data from the SQS.
"""
import logging
import os

import localstack_client.session as boto3


lambda_client = boto3.client("lambda")

function_name = 'fetch_lambda'
path = os.path.dirname(os.path.realpath(__file__))

with open(f'{path}/../deploy-package.zip', 'rb') as f:
    zipped_code = f.read()

try:
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role='arn:aws:iam::000000000000:role/lambda-role',
        Handler='aws_lambda.handler',
        Code={
            'ZipFile': zipped_code
        }
    )
except lambda_client.exceptions.ResourceConflictException:
    logging.error('Lambda already exists')
else:
    lambda_client.create_event_source_mapping(
        EventSourceArn='arn:aws:sqs::000000000000:login-queue',
        FunctionName=function_name
    )
