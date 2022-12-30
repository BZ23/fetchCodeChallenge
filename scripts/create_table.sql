/*
  After examining the sample data, a few adjustments were made to the table's
  data types rather than force values into the table through additional
  processing. Only done for the purposes of this exercise. Any real world
  changes would be discussed with stakeholders.

  Specific changes include:
    app_version - changed to a varchar to account for the various values like
    6.4.8

    create_date - changed to bigint to accomodate a unix timestamp in order to
    allow for more precision on when a user may have logged in. This will also
    help to distinguish if a user logs in multiple times per day.
*/

-- Creation of user_logins table

CREATE TABLE IF NOT EXISTS user_logins(
    user_id             varchar(128),
    device_type         varchar(32),
    masked_ip           varchar(256),
    masked_device_id    varchar(256),
    locale              varchar(32),
    app_version         varchar(256),
    create_date         bigint
);
