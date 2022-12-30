## Introduction
This document provides insight into this coding exercise and my decisions. In
addition, for each file I updated, I over-commented on its changes.

## Inventory of Added/Changed files
- data/sqs_data_record.json
- psycopg2/
- scripts/01_call_python_scripts.sh
- scripts/check_lambda_log.sh
- scripts/create_iam.py
- scripts/create_lambda.py
- scripts/create_table.py
- scripts/query_pg.sh
- scripts/setup-lambda.sh
- src/ (all files are new in this directory)
- deploy-requirements.txt
- docker-compose.yml

## How to run
To complete the task of writing to a postgres database using localstack, I opted
to do that through an AWS lambda integrated with the SQS queue as an event source.

To run this code solution, follow the same pre-requisites provided in the company
provided README, using `make start` from the main directory to start the code and
write to the database. Because localstack uses docker containers for lambdas, once
the `make start` command completes, wait for a few moments and a separate lambda
container will activate and run the code to write to Postgres.  

To provide easier access to the database and lambda logs, run the following
commands from the main directory of the git repo:

See logs: `sh scripts/check_lambda_log.sh`

Open prompt for Postgres: `sh scripts/query_pg.sh`

for the Postgres command, provide the password - `postgres` - and enter in a query
such as `select * from user_logins;` or `select count(*) from user_logins;`

Based on the data validation and transform requirements, only 99 cases are inserted
into the database.

## Design choices
Below are notes regarding my design choices that I thought required some
additional commentary.

### Database inserts
I spent some time debating the setup of how cases should be inserted to the
Postgres database. First, I had thought about the overall approach - while batch
inserts are always my preference to lower the number of calls to the DB, I wasn't
sure about how to go about doing that, either the more traditional psycopg2
approach where you manually specify the insertion query or using SQLAlchemy and
potentially pandas to utilize that functionality and insert it with a dataframe.

I think the latter has gained more usage and popularity, but I often debate its
usage - at least internally - because dataframes can be memory intensive and if
you look at SQLAlchemy queries underneath the abstraction, they can be redundant
and inefficient. But, I do recognize this approach has some appeal generally as
SQLAlchemy helps abstract out the specifics in setting up your queries for specific
database types and Pandas can assist in data manipulations.

For this type of exercise where such changes may not occur frequently, I can see
the psycopg2 approach being feasible. But, I did also try the pandas approach,
if anything I just wanted to compare the lambda elapsed time, but I found that
localstack doesn't support numphy well -
see: https://github.com/localstack/localstack/issues/646. Likewise, when I
attempted to create a deployment package for my lambda with pandas/numphy, I was
running into some errors. This sent me down a small detour looking into
whether I could add a lambda layer to support pandas but that feature is only
supported on Localstack Pro.

So, I happily continued on with the psycopg2 approach.

### Coding of the database connection and insertions
Another thing I had played with when coding for this project was potentially
dividing up the DBInserter class into a parent class it would inherit from
where the DB connection could be made. While I imagine it would be a small class
it might be somewhere where we could permit different methods of grabbing the
database credentials (either from a secret management service, environment
variables, or locally). I've seen this implemented elsewhere and while it may
run the risk of over abstraction, I found it had the nice benefit of flexibility
and separates that connection responsibility from the actual queries that might be
run on a database. While not done here, this would be something I would consider
for a production implementation, or at least a general database package to
assist with overall development.

### Event data timestamp
The database has a create time field. Without additional details, I wasn't sure
if this might mean the record creation time in the database or the user's login
event creation time. While it could have meant the database creation time
(which could be auto-populated by the database) I chose to believe it was the event
creation time to provide the analyst with more insight on when the user actually
logged in. And, to allow for more precision (assuming a user could log in multiple
times per day) I also changed the data type to a bigint to facilitate unix
timestamps. However, the only timestamp I had available was the unix timestamp
provided by SQS. This is not idea as it obviously is not a specific measure of
when the event was created and there may also be times when data must be
reprocessed through the pipeline, so any assumption that this timestamp is
approximate to event creation time would be lost. Likewise, this might also be
considered in the production implementation of this pipeline.

## Architecture
When working on this exercise, there were a few things that I would consider
changing if building a data ingestion/processing pipeline. Right now, the
lambda is overloaded with multiple responsibilities and so I might consider
moving the portion with json validation upstream closer to the ingestion point,
possibly into its own lambda. This way, events that aren't even considered can
be removed sooner in the process.

In addition, we could also look at moving out the data transformation work into
its own service, potentially updating it to permit different behavior based on
environment. And, assuming that the data transform logic may change occasionally,
it may be useful to also store what transform work has been done and what version
of it. This may be especially useful for disaster recovery. If it was ever
required, this information could be used to send data through the pipeline again.
And, as implied, this would require saving a version of the data elsewhere.
Potentially, the processed data could be placed in an S3 bucket and an S3 event
notification could trigger another lambda that would write the data to a database
(reminiscent of Snowflake's snowpipe tool which writes data files from S3 to SQS
and then magically - by way of some S3 business layer magic - ends up into a
database table).

A few other things to consider:

First, at some point in the pipeline, there should be places where filtering out
of duplicate events can be done. As part of any microservice architecture,
networking issues might occur and cause data to get re-transmitted (or outdated
configurations where the visibility timeout might be shorter than the lambda
runtime). While duplicates might be taken care of in ELT designs, its better to
remove these cases earlier in the process. Here, we could potentially use an
in-memory cache to check whether an event has gone through the pipeline in a
given window. If it has, then the data does not have to continue through the
pipeline.

Second, when errors occur or the lambda times out when connected to an SQS,
the messages aren't deleted from the queue, causing them to be reprocessed. And,
if the error is caused by its inability to handle the data, this pattern will
continue. To avoid this, adding a dead letter queue will allow for the data to
be saved elsewhere and reprocessed.

Finally, when designing any system, I would want to keep in mind the failover
requirements. If elements of the AWS cloud were to go down, how will the pipeline
respond? Usually, its been my experience that a number of health checks would be
put in place to switch the traffic flow from one region to another through Route
53 routing. This means that any pipeline that is built will have a parallel
pipeline standing by (active-passive) or one that is also accepting traffic
(active-active). This has implications for data storage choices and replication.
For instance, Dynamo has a global table feature backed up by robust replication.
All of that is to say, depending on the criticality of the data, additional
development will be required to account for failover and data availability to
partner teams.

## Fetch Provided Questions

* How would you deploy this application in production?

Presumably, deployment would be backed up by a orchestration framework like
Jenkins. Written in groovy, Jenkinsfile's would allow for custom built stages
to be done as part of the deployment, including building the AWS services as
well as running other steps that might be required such as passing tests (unit or
integration tests) as well as code coverage or different security scans.

Importantly, this framework can run infrastructure as code languages such as
terraform that can be stored in a repository (potentially with the application
code). So while localstack is a good tool to mock services, terraform (or
cloudformation) is used to save and version control the infrastructure setup.

* What other components would you want to add to make this production ready?

This question is primarily taken care of in the Architecture write up above. But,
one other thing I would want to have setup is proper monitoring to provide error
notifications so that we're aware when a problem occurs. Having proper logs and
monitoring will also let us know how well the pipeline performs as it handles
more data.

And of course - tests! My apologies for not including tests as part of this
exercise. I started writing them but decided to scrap them as I realized I was
running out of time in order to submit this exercise based on the timeframe I
shared with the people department. It also struck me as a little funny to write
tests for mocked services, but the files in the src directory would need some
unit tests.

* How can this application scale with a growing data set.

As an AWS managed service, SQS should scale automatically to handle more data.
Additionally, the number of lambdas that can run concurrently will also increase.
However, this approach will start to reach its limit as the size of the data grows
or the number of messages being transported at a given time grows beyond 120k.

Generally, this is a pretty high limit but this data could be spread out by
distributing traffic out to other pipelines based on user geolocation. Given this
pipeline is for user logins, I would expect to hit that limit but with proper
monitoring we can determine how urgent the need to redesign the system might be.

What might be of interest is whether a platform could be developed to support
multiple event types or message routing so one off pipelines become less frequent.

* How can PII be recovered later on?

PII information is always treated with importance and whether it is stored in its
entirety should be discussed with business stakeholders and any security specialists.
Assuming that a copy of the original data can not be kept, the original PII could be
recovered as long as the transformation logic is fully understood and can be backwards
engineered. As discussed above, this would require that we also keep meta data on
what version of a data transform function is run and the actual date of when this logic
was applied.
