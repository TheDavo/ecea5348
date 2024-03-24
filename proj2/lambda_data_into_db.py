import logging
import pymysql
import json
import boto3
import os
from botocore.exceptions import ClientError
import sys

# Code used from tutorial to insert data into an AWS RDS db
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-lambda-tutorial.html

# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/


def get_secret():

    secret_name = "ecea5348/secrets"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    print("session made")

    try:
        print("getting secret values")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        print("secret values got")
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return secret


secret = json.loads(get_secret())

db_username = secret.get('username')
db_password = secret.get('password')
db_name = secret.get('dbname')
host = os.environ.get("RDSHOST")
table = "SensorData"


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Create the database connection outside of handler events to allow
# connections to be re-used by subsequent function invocations.

try:
    conn = pymysql.connect(
        host=host,
        user=db_username,
        passwd=db_password,
        db=db_name,
        connect_timeout=5
    )

except pymysql.MySQLError as e:
    logger.error(
        "ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit(1)


logger.info("SUCCESS: Connection to RDS for MySQL instance succeeded.")


def lambda_handler(event, context):
    """
    Creates a database if one does not exist and adds pseudo sensor data to it.
    """

    datetime = event['datetime']
    temperature = float(event['temperature'])
    humidity = float(event['humidity'])

    insert_data_str = f"""
    INSERT INTO {table} (datetime, temperature_degC, humidity_pcent)
    values (%s, %s, %s)
    """

    create_table_str = f"""
        CREATE TABLE IF NOT EXISTS {table} (
        id int AUTO_INCREMENT,
        datetime varchar(255),
        temperature_degC float,
        humidity_pcent float,
        primary key (id)
    )
    """

    with conn.cursor() as cur:
        cur.execute(create_table_str)
        cur.execute(insert_data_str, (datetime, temperature, humidity))

    conn.commit()

    return "Added item to RDS for MySQL table"
