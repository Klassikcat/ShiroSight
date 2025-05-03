import orjson


def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }
