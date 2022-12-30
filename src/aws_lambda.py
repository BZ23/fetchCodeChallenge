import json
import logging

from jsonschema import Draft4Validator

from BaseProcessor import BaseProcessor
from config import db_params, insert_query, login_schema, processors
from DBInserter import DBInserter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """AWS lambda event handler with event source mapping from SQS login-queue.
    Consumes data from SQS, evaluates whether a record is valid for processing,
    if so, it modifies that record, and inserts to a Postgres DB.

    Args:
        event [str]: JSON formatted string holding the data received by the
            lambda.
        context [str]: Meta data concerning the lambda's execution from AWS.

    Returns:
        None
    """
    validator = Draft4Validator(login_schema)
    records = []
    for record in event['Records']:
        # for each record, evaluate whether the data received is valid based on
        # a basic schema. This will both protect against invalid cases being
        # processed and inserted, but also from errors that may result due to
        # a few bad records during the batch insert to the database. If such
        # errors were to occur, valid cases in the batch may not get inserted.
        login_event = json.loads(record['body'])
        errors = [error for error in validator.iter_errors(login_event)]
        if not errors:
            # here, the data manipulation for IP and device_id are conducted as
            # a series of processor classes. This is meant to allow for the
            # ability to change the code when needed, to either add or remove
            # additional transoformation logic or apply different transforms to
            # different environments depending on the processors sent in to be
            # run
            processor = BaseProcessor(
                data=record,
                processors=processors
            )
            processor.process_data()
            records.append(processor.data_transform)
        else:
            logging.error({
                "event": "Invalid event",
                "message": f"Errors - {errors}"
            })
    # beginning the database insertion logic. There are likely different coding
    # methods or tools to accomplish this. I've put some additional context in
    # the readme regarding my choices.
    db_inserter = DBInserter(
        data=records,
        db_params=db_params
    )
    db_inserter.batch_insert(query=insert_query)
