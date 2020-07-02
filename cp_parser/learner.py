#!/bin/env python3
import boto3
import pandas
import time 
import csv
import athena_from_s3
import json
from collections import defaultdict
from pprint import pprint as pp

username = 'akurow'
params = {
    'region' : 'eu-west-1',
    'database' : 'cloudtrail',
    'bucket' : 'iam-manager-cloudtrails310cd22f2-faslq2t36wt4',
    'path'  : 'athena_out',
    'query': f'SELECT * FROM "cloudtrail"."trail_logs" WHERE "useridentity"."arn"  = \'arn:aws:iam::789552300344:user/{username}\''
}
session = boto3.session.Session()
location, data= athena_from_s3.query_results(session, params)
print("Locations", location)
print("Result Data: ")
pp(data['Rows'][1]['Data'])


rights = defaultdict(int)


iterate = len(data['Rows'])
for i in range(1,iterate):
    row = data['Rows'][i]

    e2 = row['Data'][4]['VarCharValue']
    e1 = row['Data'][3]['VarCharValue'].split('.')[0]
    reg = row['Data'][5]['VarCharValue']
    param = row['Data'][10]['VarCharValue']
    acc_id = row['Data'][19]['VarCharValue']
    right =  f'arn:aws:{e1}:{reg}:{acc_id}:{e2}:*'
    rights[right] += 1


print(f"Single: {rights[1]}\n\n")
rights_list = [key for key, value in rights.items() if value > 0 and "eu-west-1" in key]
pp(rights_list)

with open('policy_template.json', 'r+') as f:
    data = json.load(f)
    for right in rights_list:
        right = right.split(':')

        action = f"{right[2]}:{right[5]}"
        dest = data['Statement'][0]['Action']
        if action not in dest:
            dest.append(action)
        
        resource = f"{right[0]}:{right[1]}:{right[2]}:{right[3]}:{right[4]}:*"
        dest = data['Statement'][0]['Resource']
        if resource not in dest:
            dest.append(resource)
    
    pp(data)
