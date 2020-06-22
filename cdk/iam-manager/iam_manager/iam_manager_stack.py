from aws_cdk import (
    core,
    aws_apigateway as agw,
    aws_lambda as lambda_,
    aws_cloudtrail as cloudtrail,
    aws_glue as glue,
    aws_athena as athena,
    aws_s3 as s3
)


class IamManagerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role_changer = lambda_.Function(self,"RoleChanger",
            runtime = lambda_.Runtime.PYTHON_3_8,
            code =  lambda_.Code.from_asset("lambdas/switcher"),
            handler = "main.handler",
        )

        api = agw.RestApi(self, "widgets-api",
            rest_api_name="Widget Service",
            description="This service serves widgets.")

        get_widgets_integration = agw.LambdaIntegration(role_changer,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", get_widgets_integration) 

        # CloudTrail 
        bucket = s3.Bucket(self,'TrailBucket')
        tail = cloudtrail.Trail(self,'CloudTrail',bucket=bucket)

        db_name = 'cloudtrail'
        db = glue.Database(self,'cloudtrail',database_name=db_name)

        awg = core.CfnResource(self,'AthenaWorkGroup',
            type = "AWS::Athena::WorkGroup",
            properties={
                "Name" : "IAMManagerWorkgroup",
                "State":"ENABLED",
                "WorkGroupConfiguration":{
                    "ResultConfiguration":{
                        "OutputLocation":f"s3://{bucket.bucket_name}/"
                    }
                }

            }
            )
        core.CfnOutput(self,'BucketName',value=bucket.bucket_name)






    
        



