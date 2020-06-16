# Internal Modules
import os

# External Modules
import boto3  # available as default in AWS Lambda


learning_mode = os.environ['LEARNING_MODE']
learning_group = os.environ['LEARNING_GROUP']
username = os.environ['USERNAME']


def handler(event, context):    
    # Start session and select IAM client
    session = boto3.session.Session()
    iam = session.client('iam')
    success = False

    # Mode switcher
    if learning_mode:
        try:
            iam.add_user_to_group(
                GroupName=learning_group,
                UserName=username
            )
            success = True
            print(f"User {username} has been added to {learning_group} group.")
        except:
            print(f"User {username} is already added to {learning_group} group.")
    else:
        try:
            iam.remove_user_from_group(
                GroupName=learning_group,
                UserName=username
            )
            success = True
            print(f"User {username} has been removed from {learning_group} group.")
        except:
            print(f"User {username} is not in {learning_group} group.")

    
    
    if success:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain'
            },
            'body': 'Lambda finished with code 0.'
        }
    else:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/plain'
            },
            'body': 'Lambda finished with code 1.'
        }
