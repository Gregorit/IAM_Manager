#!/bin/env python3
import boto3
import pandas
import time 
import csv
import athena_from_s3
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
print(data)
