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

    # Mode switcher
    if "user" in arn_fragments[5]:
        username = arn_fragments[5].strip('/')[1]

        try:
            users_groups = iam.list_groups_for_user(
                UserName=username
            )

            for group in users_groups['Groups']:
                iam.remove_user_from_group(
                    GroupName=group['GroupName'],
                    UserName=username
                )
        except iam.exceptions.NoSuchEntityException:
            pass

        iam.add_user_to_group(
            GroupName=learning_group,
            UserName=username
        )
        print(f"User {username} has been added to {learning_group} group.")
    
    elif "role" in arn_fragments[5]:
        rolename = arn_fragments[5].strip('/')[1]
        
        try:
            role_policies = iam.list_role_policies(
                RoleName=rolename
            )
            
            for policy in role_policies['PolicyNames']:
                iam.detach_role_policy(
                    RoleName=rolename,
                    PolicyArn=f'{arn_fragments[0]}:{arn_fragments[1]}:iam::{arn_fragments[4]}:policy/{policy}'
                )
        except iam.exceptions.NoSuchEntityException:
            pass
        
        iam.attach_role_policy(
            RoleName=rolename,
            PolicyArn=f'{arn_fragments[0]}:{arn_fragments[1]}:iam::{arn_fragments[4]}:policy/{learning_policy}'
        )
        print(f"Policy {learning_policy} has been added to {rolename} role.")


    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Lambda finished with code 0.'
    }
