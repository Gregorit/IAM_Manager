# Internal Modules
import os

# External Modules
import boto3  # available as default in AWS Lambda


role_user_group_arn = event['queryStringParameters']['arn']
learning_group = 'administrator'
learning_policy = 'AdministratorAccess'


def handler(event, context):
    arn_fragments = role_user_group_arn.split(':')

    # Start session and select IAM client
    session = boto3.session.Session()
    iam = session.client('iam')
    success = True

    # Mode switcher
    if arn_fragments[5] == "user":
        username = arn_fragments[5].strip('/')[1]
        try:
            iam.add_user_to_group(
                GroupName=learning_group,
                UserName=username
            )
            print(f"User {username} has been added to {learning_group} group.")
        except:
            print(f"User {username} is already added to {learning_group} group.")
    
    elif arn_fragments[5] == "role":
        rolename = arn_fragments[5].strip('/')[1]
        try:
            iam.attach_role_policy(
                RoleName=rolename,
                PolicyArn=learning_policy
            )
        except:
            print(f"Policy {learning_policy} has been added to {rolename} role.")
    # else:
    #     try:
    #         iam.remove_user_from_group(
    #             GroupName=learning_group,
    #             UserName=username
    #         )
    #         print(f"User {username} has been removed from {learning_group} group.")
    #     except:
    #         print(f"User {username} is not in {learning_group} group.")
    #         success = False

    # CodeBuild launch
    try:
        print(f"Launching CodeBuild...")
        codebuild = session.client('codebuild')
        codebuild.start_build(
            projectName = "mainpipelineprojectA75A748F-Q84zgcuZfXVF",
            artifactsOverride={
                'type': 'CODEPIPELINE'
            }
        )
    except:
        print("CodeBuild launching failed!")
        success = False


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
