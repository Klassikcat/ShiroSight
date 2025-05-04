import boto3
import autogen


def create_client():
    session = boto3.Session(profile_name="blackcircles")
    client = session.client("bedrock-runtime")
    return client


def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }
