"""Series of variables used throughout the lambda's source code."""

from DeviceIDProcessor import DeviceIDProcessor
from IPProcessor import IPProcessor


login_schema = {
    "type" : "object",
    "properties" : {
        "user_id": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },
        "app_version": {"type": "string"},
        "device_type": {"type": "string"},
        "ip": {"type": "string"},
        "locale": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },
        "device_id": {"type": "string"}
    },
    "required": [
        "user_id",
        "app_version",
        "device_type",
        "ip",
        "locale",
        "device_id"
    ]
}

processors = [
    DeviceIDProcessor,
    IPProcessor
]

db_params = {
    'host': 'postgres',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'dbname': 'postgres'
}

insert_query = """
    INSERT INTO user_logins
    VALUES
        (
            %(user_id)s,
            %(device_type)s,
            %(masked_ip)s,
            %(masked_device_id)s,
            %(locale)s,
            %(app_version)s,
            %(create_date)s
        )
"""
