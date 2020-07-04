import os
import boto3

def handler(event, context): 
  arn = event['queryStringParameters']['arn']
  codebuild_name = os.environ['codebuild']

  client = boto3.client('codebuild',region_name='eu-west-1')

  response = client.start_build(
      projectName=codebuild_name,

      environmentVariablesOverride=[
          {
              'name': 'arn',
              'value': arn,
              'type': 'PLAINTEXT'
          },
      ]

  )
  return {
          'statusCode': 200,
          'headers': {
              'Content-Type': 'text/html'
          },
          'body': f'Started Learning proces for ARN:{arn}'
  }