
import boto3
import base64
import hashlib
import hmac
import json
import logging
import os

from botocore.exceptions import ClientError

from CommandProcessor import CommandProcessor

logger = logging.getLogger()
LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
logging.basicConfig(level=LOGLEVEL)


def get_secret_from_secret_manager(secret_name):

    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    return json.loads(get_secret_value_response['SecretString'])['key']

slack_key = get_secret_from_secret_manager('botty-api-key')
slack_signing_key = get_secret_from_secret_manager('botty-signing-key')

def verify_slack_request(slack_signature=None, slack_request_timestamp=None, request_body=None):
    ''' Form the basestring as stated in the Slack API docs. We need to make a bytestring. '''
    base_string = f"v0:{slack_request_timestamp}:{request_body}".encode('utf-8')

    ''' Make the Signing Secret a bytestring too. '''
    slack_signing_secret = bytes(slack_signing_key, 'utf-8')

    ''' Create a new HMAC "signature", and return the string presentation. '''
    my_signature = 'v0=' + hmac.new(slack_signing_secret, base_string, hashlib.sha256).hexdigest()

    ''' Compare the the Slack provided signature to ours.
    If they are equal, the request should be verified successfully.
    Log the unsuccessful requests for further analysis
    (along with another relevant info about the request). '''
    if hmac.compare_digest(my_signature, slack_signature):
        return True
    else:
        logger.warning(f"Verification failed. my_signature: {my_signature}")
        return False

def error500(message):
    return {
            "statusCode": 500,
            "body": message
        }

def response400(message):
    return {
            "statusCode": 400,
            "body": message
        }

def response200(message):
    return {
            "statusCode": 400,
            "body": message
        }

def handler(event, context):

    logger.warning(event)

    ''' Grab signature verification data '''
    slack_signature = event['headers']['X-Slack-Signature']
    slack_request_timestamp = event['headers']['X-Slack-Request-Timestamp']

    ''' Verify request signature '''
    if not verify_slack_request(slack_signature, slack_request_timestamp, event['body']):
        logger.info('Request failed signature verification')
        return response400('Request failed signature verification')

    ''' Error out on slack retries '''
    if 'X-Slack-Retry-Num' in event['headers']:
        logger.warning('ignoring retry request')
        return error500('ignore retries')

    ''' get call type '''
    if 'body' not in event:
        return error500("request is missing body")

    request_body = json.loads(event['body'])

    if 'type' not in request_body:
        return error500("request does not contain call type")

    call_type = request_body['type']

    if call_type == 'url_verification':

        ''' respond with challenge string from request body '''
        return {
            "statusCode": 200,
            "body": request_body['challenge']
        }

    elif call_type == 'event_callback':

        CommandProcessor(slack_key, request_body)

    
    else:

        return error500("unknown call type")

event = {'resource': '/event-handler', 'path': '/event-handler', 'httpMethod': 'POST', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-Country': 'US', 'Content-Type': 'application/json', 'Host': 'zdmg6oh0wd.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'Slackbot 1.0 (+https://api.slack.com/robots)', 'Via': '1.1 ed8e6c4476f2632eef2c7ce856161af0.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': '8G-TvYya1SXnUctQkHgT5t-WIPibcwFj19MJYIxDQo_1LjAAbVELlA==', 'X-Amzn-Trace-Id': 'Root=1-5ea12529-ff9fc95751a301f2f67da38d', 'X-Forwarded-For': '54.167.28.190, 70.132.33.75', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https', 'X-Slack-Request-Timestamp': '1587619113', 'X-Slack-Signature': 'v0=0a9d0bcbed663a3c879bc9b57d37181bad7b46e5dcae4f5441cfe209e95a7088'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip,deflate'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-Country': ['US'], 'Content-Type': ['application/json'], 'Host': ['zdmg6oh0wd.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['Slackbot 1.0 (+https://api.slack.com/robots)'], 'Via': ['1.1 ed8e6c4476f2632eef2c7ce856161af0.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['8G-TvYya1SXnUctQkHgT5t-WIPibcwFj19MJYIxDQo_1LjAAbVELlA=='], 'X-Amzn-Trace-Id': ['Root=1-5ea12529-ff9fc95751a301f2f67da38d'], 'X-Forwarded-For': ['54.167.28.190, 70.132.33.75'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https'], 'X-Slack-Request-Timestamp': ['1587619113'], 'X-Slack-Signature': ['v0=0a9d0bcbed663a3c879bc9b57d37181bad7b46e5dcae4f5441cfe209e95a7088']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'rjpsq7', 'resourcePath': '/event-handler', 'httpMethod': 'POST', 'extendedRequestId': 'LbK-dHloIAMFXSA=', 'requestTime': '23/Apr/2020:05:18:33 +0000', 'path': '/dev/event-handler', 'accountId': '850513161386', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': 'zdmg6oh0wd', 'requestTimeEpoch': 1587619113245, 'requestId': '471ce0d5-cf14-46bb-af53-2a92d13e22e2', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '54.167.28.190', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Slackbot 1.0 (+https://api.slack.com/robots)', 'user': None}, 'domainName': 'zdmg6oh0wd.execute-api.us-east-1.amazonaws.com', 'apiId': 'zdmg6oh0wd'}, 'body': '{\"token\":\"Klyhi1DC44Fo4mt2gtdUkfRL\",\"challenge\":\"mPRyAXpx0zUnFtHh62KkOckWrBOMIK6nlKEqAB99NlawhIMd6wV8\",\"type\":\"url_verification\"}', 'isBase64Encoded': False}
print(handler(event, None))