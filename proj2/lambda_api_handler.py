import json
import os
import pymysql
import sys
import boto3
import logging
from botocore.exceptions import ClientError


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
    Handles the API for this course project.
    Returns data from the sensor MySQL database.

    Query parameters:
    count (int): returns count number of entries from database, if count is
    greater than the amount of data available, returns max amount
    """

    condition = "WHERE"

    # Count is the amount of data to retrieve from the latest set of data
    try:
        count = int(event["queryStringParameters"]["count"])
    except Exception as e:
        logger.info("Error parsing query parameter count: setting to default 1")
        logger.info(e)
        count = 1

    # Allow the user to also filter by a particular ID
    try:
        id = int(event["queryStringParameters"]["id"])
        condition += f" id={id}"
    except Exception as e:
        logger.info("Error parsing query parameter id")
        logger.info(e)
        id = None
        condition += ""

    get_data = f"""
        SELECT * FROM {table}
    """
    order_by = "ORDER BY id DESC"
    limit = f"LIMIT {count}"

    if condition == "WHERE":
        full_query = get_data + " " + order_by + " " + limit
    else:
        full_query = get_data + " " + condition + " " + order_by + " " + limit

    with conn.cursor() as cur:
        cur.execute(full_query)
        rows = cur.fetchall()

    content = {}
    payload = []

    # Make the rows list[list] into a dictionary
    for row in rows:
        content = {"id": row[0], "datetime": row[1],
                   "temperature_degC": row[2], "humidity_pcent": row[3]}
        payload.append(content)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "*/*"
        },
        "body": json.dumps(payload),
    }
