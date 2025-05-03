import boto3
import autogen


def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }
