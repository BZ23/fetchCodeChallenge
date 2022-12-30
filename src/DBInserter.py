import logging

import psycopg2
from psycopg2.extras import execute_batch

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DBInserter:
    def __init__(self, data, db_params):
        """Class for the connection and insertion of records to a database.

        Args:
            data [list]: a list of dictionaries. Each dictionary holds the
                values to be inserted to the database where each dict key
                represents a column of the database.
            db_params [dict]: A dictionary holding the parameters used to
                connect to the Postgres database, including - host [str], port
                [int], user [str], password [str], and dbname [str].
        """
        self.data = data
        self.db_params = db_params

    def pg_conn(self):
        """Establishes connection with Postgres database using database
        parameters provided during class instantiation.

        Returns:
            Postgres database connection
        """
        try:
            conn = psycopg2.connect(**self.db_params)
        except Exception as exc:
            logger.error({
                "event": "Exception",
                "message": f"{exc}"
            })
        else:
            return conn

    def batch_insert(self, query):
        """Batch inserts records to database."""
        conn = self.pg_conn()
        cur = conn.cursor()

        try:
            execute_batch(cur, query, self.data)
            conn.commit()

            logger.info({
                "event": "DB Insert",
                "message": f"Number of records inserted: {len(self.data)}"
            })
        except Exception as exc:
            logger.error({
                "event": "Exception",
                "message": f"{exc}"
            })
        finally:
            cur.close()
            conn.close()
