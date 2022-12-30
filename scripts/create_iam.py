"""Script to create the necessary IAM roles/policies for a lambda with event
source mapping to an SQS.
"""
import json
import logging
import os

import localstack_client.session as boto3


iam = boto3.client("iam")

path = os.path.dirname(os.path.realpath(__file__))
role = f'{path}/../IAM/lambda-role.json'
policy = f'{path}/../IAM/lambda-policy.json'

role_doc = open(role).read()
policy_doc = open(policy).read()
role_name = 'lambda-role'

try:
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=role_doc
    )
except iam.exceptions.EntityAlreadyExistsException:
    logging.error('IAM role already exists')
except Exception as exc:
    logging.error(f'Exception: {exc}')


try:
    policy_response = iam.create_policy(
        PolicyName='lambda-policy',
        PolicyDocument=policy_doc
    )
except iam.exceptions.EntityAlreadyExistsException:
    logging.error('IAM policy already exists')
except Exception as exc:
    logging.error(f'Exception: {exc}')
else:
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_response['Policy']['Arn']
    )
