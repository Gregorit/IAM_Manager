import os


def handler(event, context): 
  arn = event['queryStringParameters']['arn']

  return {
          'statusCode': 200,
          'headers': {
              'Content-Type': 'text/html'
          },
          'body': f'Work in {arn}'
  }