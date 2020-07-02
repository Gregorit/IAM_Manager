#!/bin/env python3
import boto3
import pandas
import time 
import csv
import athena_from_s3
from collections import defaultdict
params = {
     'region' : 'eu-west-1',
     'database' : 'cloudtrail',
     'bucket' : 'iam-manager-cloudtrails310cd22f2-faslq2t36wt4',
     'path'  : 'athena_out',
     'query': 'SELECT * FROM "cloudtrail"."trail_logs" WHERE "useridentity"."arn"  = \'arn:aws:iam::789552300344:user/akurow\''
     }
session = boto3.session.Session()
location, data= athena_from_s3.query_results(session, params)
print("Locations", location)
print("Result Data: ")

rights = defaultdict(int)


iterate = len(data['Rows'])
for i  in range(1,iterate):
     row = data['Rows'][i]

     e2 = row['Data'][4]['VarCharValue']
     e1 = row['Data'][3]['VarCharValue'].split('.')[0]
     reg = row['Data'][5]['VarCharValue']
     param = row['Data'][10]['VarCharValue']
     right =  f'arn:aws:{e1}:{reg}:123412341234:{e2}:*'
     rights[right] += 1

from pprint import pprint as pp
pp(rights)
