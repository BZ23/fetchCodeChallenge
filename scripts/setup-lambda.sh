#!/bin/sh
################################################################################
# Script to create the lambda deployment package as well as run the python
# script that will create the lambda using this deploy package.
#
# Note that the deploy package will both install requirements listed from the
# deploy-requirements.txt file as well as a local pacage created for psycopg2.
# Similar to AWS, this libary has difficulties installing during setup, so it
# was added locally. See:
# https://github.com/jkehler/awslambda-psycopg2
################################################################################

# create code deployment package
cd ~/../tmp
chmod +x src/aws_lambda.py
mkdir package
pip install -r deploy-requirements.txt --target ./package
cp -r psycopg2 package/
cd package
zip -r ../deploy-package.zip .
cd ..
zip -j deploy-package.zip src/*

# run python script that will create lambda with event source mapping to SQS
cd scripts/
python -m create_lambda
