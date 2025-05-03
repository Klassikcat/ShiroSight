import boto3


def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }
