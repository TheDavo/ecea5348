import boto3
from dotenv import dotenv_values

config = dotenv_values(".env")

sqs = boto3.client("sqs")

queue_url = config["SQS_QUEUE_URL"]

response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
)

# Check if the response has any messages received
if "Messages" in response.keys():
    for message in response["Messages"]:
        print(message)

        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message["ReceiptHandle"]
        )
