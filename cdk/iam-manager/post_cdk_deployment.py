#!/bin/env python3
import json
import configparser
import boto3
import zipfile
import os

# Read Config File
config = configparser.ConfigParser()
config.read('config.ini')

account_id=config.get('MAIN','account_id')


with open('out.json') as f:
    array = json.load(f)

# After CDK is complete, we need to create table in Athena

query = f"""
CREATE EXTERNAL TABLE trail_logs (
    eventversion STRING,
    useridentity STRUCT<
                type:STRING,
                principalid:STRING,
                arn:STRING,
                accountid:STRING,
                invokedby:STRING,
                accesskeyid:STRING,
                userName:STRING,
    sessioncontext:STRUCT<
    attributes:STRUCT<
                mfaauthenticated:STRING,
                creationdate:STRING>,
    sessionissuer:STRUCT<  
                type:STRING,
                principalId:STRING,
                arn:STRING, 
                accountId:STRING,
                userName:STRING>>>,
    eventtime STRING,
    eventsource STRING,
    eventname STRING,
    awsregion STRING,
    sourceipaddress STRING,
    useragent STRING,
    errorcode STRING,
    errormessage STRING,
    requestparameters STRING,
    responseelements STRING,
    additionaleventdata STRING,
    requestid STRING,
    eventid STRING,
    resources ARRAY<STRUCT<
                ARN:STRING,
                accountId:STRING,
                type:STRING>>,
    eventtype STRING,
    apiversion STRING,
    readonly STRING,
    recipientaccountid STRING,
    serviceeventdetails STRING,
    sharedeventid STRING,
    vpcendpointid STRING
)
ROW FORMAT SERDE 'com.amazon.emr.hive.serde.CloudTrailSerde'
STORED AS INPUTFORMAT 'com.amazon.emr.cloudtrail.CloudTrailInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://{array['iam-manager']['BucketName']}/AWSLogs/{account_id}/CloudTrail/';  
"""
client = boto3.client('athena',region_name=config.get('MAIN','region'))


response = client.list_table_metadata(
    DatabaseName='cloudtrail',
    CatalogName ='AwsDataCatalog'
)
table = [t['Name'] for t in response['TableMetadataList'] if t['Name'] == 'trail_logs']
if 'trail_logs' not in table:
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': 'cloudtrail'
        },
        WorkGroup='IAMManagerWorkgroup'
    )

# We must make sure that we have artifacts for CodePipeline
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
# Zip it
zipf = zipfile.ZipFile('pipeline.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('../../cp_parser', zipf)
zipf.close()
# Send it to bucket
s3 = boto3.client('s3')
s3.upload_file('pipeline.zip',array['iam-manager']['BucketName'],'pipeline/learner.zip')
