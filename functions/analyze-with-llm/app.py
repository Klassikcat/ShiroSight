import boto3
from autogen.openai import OpenAI


def create_client(client: str):
    return


def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }
