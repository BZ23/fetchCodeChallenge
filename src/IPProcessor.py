import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class IPProcessor:
    def __init__(self, data):
        """IP field processor that masks the original value.

        Args:
            data [dict]: The event data that requires processing.
        """
        self.data = data
        self.process_data()

    def is_valid(self):
        """Provides light validation regarding whether the event data should be
        processed by checking the ddata received and whether it contains the
        important fields to be modified.

        Returns:
            Boolean
        """
        return isinstance(self.data, dict) and self.data.get('ip')

    def process_data(self):
        """Conducts the data modifaction after validating whether the data
        should be updated.
        """
        if self.is_valid():
            values = [int(n)-1 for n in self.data['ip'].split('.')]
            self.data['masked_ip'] = '.'.join(str(n) for n in values)
            del self.data['ip']
        else:
            user_id = self.data.get('user_id')
            logger.info({
                "event": "Data Processing",
                "message": f"Record invalid for processing. User ID: {user_id}"
            })
