#!/bin/env python3
import boto3
import pandas
import time 
import csv
import athena_from_s3
import json
from collections import defaultdict
from pprint import pprint as pp
from botocore.exceptions import ClientError
import os


# role_user_group_arn = "arn:aws:iam::789552300344:user/akurow"

# role_user_group_arn = event['queryStringParameters']['arn']
role_user_group_arn = os.environ['arn']
region_name =  os.environ['region_name']
athena_database = os.environ['athena_database']
bucket = os.environ['bucket']

arn_fragments = role_user_group_arn.split(':')
name = arn_fragments[5].split('/')[1]

def handler():
    print("External variables:"
    f"role_user_group_arn: {role_user_group_arn} \n"
    f"region_name: {region_name}\n"
    f"athena_database: {athena_database}\n"
    f"bucket: {bucket}\n\n")

    params = {
        'region' : region_name,
        'database' : athena_database,
        'bucket' : bucket,
        'path'  : 'athena_out',
        'query': f'SELECT * FROM "cloudtrail"."trail_logs" WHERE "useridentity"."arn" = \'{role_user_group_arn}\''
        }
    
    session = boto3.session.Session()
    location, data= athena_from_s3.query_results(session, params)
    print("Locations", location)

    print("Result Data: ")
    pp(data['Rows'][1]['Data'])


    rights = defaultdict(int)

    ignore_list = ["signin", "tagging", "monitoring"]
    iterate = len(data['Rows'])
    for i in range(1,iterate):
        row = data['Rows'][i]
        if row['Data'][3]['VarCharValue'].split('.')[0] in ignore_list:
            continue

        e1 = row['Data'][3]['VarCharValue'].split('.')[0]
        e2 = row['Data'][4]['VarCharValue']
        reg = row['Data'][5]['VarCharValue']
        # param = row['Data'][10]['VarCharValue']
        acc_id = row['Data'][19]['VarCharValue']
        right =  f'arn:aws:{e1}:{reg}:{acc_id}:{e2}:*'
        rights[right] += 1


    print(f"Single: {rights[1]}\n\n")
    rights_list = [key for key, value in rights.items() if value > 0]
    pp(rights_list)


    generated_policy = {
        "Version": "2012-10-17",
        "Statement": []
        }

    services_list = []
    for right in rights_list:
        right = right.split(':')

        if right[2] not in services_list:
            services_list.append(right[2])
            generated_policy['Statement'].append({
                "Effect": "Allow",
                "Action": [],
                "Resource": []
                })


        action = f"{right[2]}:{right[5]}"
        dest = generated_policy['Statement'][services_list.index(right[2])]['Action']
        if action not in dest:
            dest.append(action)
        
        resource = f"{right[0]}:{right[1]}:{right[2]}:::*"
        dest = generated_policy['Statement'][services_list.index(right[2])]['Resource']
        if resource not in dest:
            dest.append(resource)


    # Check if policy exists, remove it if yes
    try:
        iam = session.client('iam')
        iam.create_policy(
            PolicyName = "generated-policy",
            PolicyDocument = json.dumps(generated_policy)
        )
    except ClientError:
        iam = session.client('iam')
        att_groups = iam.list_entities_for_policy(
            PolicyArn=f'{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy',
            EntityFilter='Group'
        )
        att_roles = iam.list_entities_for_policy(
            PolicyArn=f'{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy',
            EntityFilter='Role'
        )

        # Detach policy
        for group in att_groups['PolicyGroups']:
            iam = boto3.resource('iam')
            group = iam.Group(group['GroupName'])
            group.detach_policy(
                PolicyArn=f'{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy'
            )
        for role in att_roles['PolicyRoles']:
            iam = boto3.resource('iam')
            role = iam.Role(role['RoleName'])
            role.detach_policy(
                PolicyArn=f'{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy'
            )

        # Remove old policy
        iam = session.client('iam')
        iam.delete_policy(
            PolicyArn=f"{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy"
        )
        # Create new policy
        iam.create_policy(
            PolicyName = "generated-policy",
            PolicyDocument = json.dumps(generated_policy)
        )
    
    if "user" in arn_fragments[5]:
        # Remove user from all groups
        iam = session.client('iam')
        users_groups = iam.list_groups_for_user(
            UserName=name
        )

        for group in users_groups['Groups']:
            iam.remove_user_from_group(
                GroupName=group['GroupName'],
                UserName=name
            )

        iam.add_user_to_group(
            GroupName='tester',
            UserName=name
        )

        # Attach policy to group
        iam = boto3.resource('iam')
        group = iam.Group('tester')
        group.attach_policy(
            PolicyArn=f'{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy'
        )

    elif "role" in arn_fragments[5]:
        iam = session.client('iam')
        role_policies = iam.list_role_policies(
            RoleName=name
        )
        
        for policy in role_policies['PolicyNames']:
            iam.remove_user_from_group(
                GroupName=policy,
                UserName=name
            )
        
        iam.attach_role_policy(
            RoleName=name,
            PolicyArn=f'{right[0]}:{right[1]}:iam::{right[4]}:policy/generated-policy'
        )


    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Learner finished with code 0.'
    }

handler()
