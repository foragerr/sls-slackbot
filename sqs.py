import boto3
import json

QUEUE_NAME = 'deployqueue.fifo'

def send_message(message :str):
    # Get the service resource
    sqs = boto3.resource('sqs')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    # Create a new message
    response = queue.send_message(MessageBody=message, MessageGroupId='deploy')

    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))

def peek_messages():
    # Get the service resource
    sqs = boto3.resource('sqs')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)
    queue.load()

    deployitems = []
    # Process messages by printing out body and optional author name
    for message in queue.receive_messages(    
            MaxNumberOfMessages=10,
            VisibilityTimeout=1
        ):

        # Add message to list
        deployitems.append(json.loads(message.body))

    return deployitems

# Tests
# print(peek_messages())

# for i in range(5):
#     deploypacket = { 'name': f"Service{i}", 'versionfrom': 'v1.0.0', 'versionto': 'v2.0.0', 'requestor': f"John {i}"}
#     send_message(json.dumps(deploypacket))