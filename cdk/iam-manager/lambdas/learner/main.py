def handler(event, context): 
    arn = event['queryStringParameters']['arn']    
    return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain'
            },
            'body': f'Learner !.{arn}'
    }