import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseProcessor:
    def __init__(self, data, processors):
        """Platform from which additional data mungers may be added and
        initiated.

        Once instantiated, this class will pull the event data from the overall
        JSON formatted string sent by the consumer and make it available for the
        processors.

        Args:
            data [str]: JSON formatted string of the received event data from
                the producer, including any metadata.
            processors [list]: List of class instatiations that will each
                process the event data to either filter or enrich the data event.
        """
        self.data = data
        self.data_transform = json.loads(self.data['body'])
        self.processors = processors

    def add_time(self):
        """Enriches data with unix timestamp received from SQS."""
        try:
            self.data_transform['create_date'] = self.data['attributes']['SentTimestamp']
        except KeyError:
            logger.error({
                "event": "Exception",
                "message": "SentTimestamp key not found. Create_date not added."
            })

    def process_data(self):
        """Main method used to run all data transformations."""
        self.add_time()
        for processor in self.processors:
            self.data_transform = processor(self.data_transform).data
