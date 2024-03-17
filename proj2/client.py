import boto3
import json
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
    amt_messages = len(response["Messages"])
    for i, message in enumerate(response["Messages"]):
        body = json.loads(message["Body"])

        print("Message", i+1, "of", amt_messages, "messages")
        for key, value in body.items():
            print("\t", key, "->", value)

        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message["ReceiptHandle"]
        )
else:
    print("No messages available from SQS Queue")
