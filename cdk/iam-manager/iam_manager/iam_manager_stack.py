from aws_cdk import (
    core,
    aws_apigateway as agw,
    aws_lambda as lambda_,
    aws_cloudtrail as cloudtrail,
    aws_glue as glue,
    aws_athena as athena,
    aws_s3 as s3,
    aws_iam as iam,
    aws_route53 as route53,
    aws_certificatemanager as certmanager,
    aws_cloudfront  as cloudfront,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as pipeline_actions
)
# from static_website import StaticWebsite


class IamManagerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
        region_name: str, db_name: str,
        **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # CloudTrail 
        bucket = s3.Bucket(self,'TrailBucket',
            versioned = True
        )
        tail = cloudtrail.Trail(self,'CloudTrail',bucket=bucket)

        db = glue.Database(self,'cloudtrail',database_name=db_name)

        awg = core.CfnResource(self,'AthenaWorkGroup',
            type = "AWS::Athena::WorkGroup",
            properties={
                "Name" : f"{db_name}",
                "State":"ENABLED",
                "WorkGroupConfiguration":{
                    "ResultConfiguration":{
                        "OutputLocation":f"s3://{bucket.bucket_name}/athena_output/"
                    }
                }

            }
            )

        # Pipeline for Working on Data
        project = codebuild.Project(self, 'learner_build',
            build_spec = codebuild.BuildSpec.from_source_filename('buildspec.yml'),
            environment_variables = {
                'arn':{'value':'-- Pur ARN Here --'},
                'athena_database' : {'value':db_name},
                'region_name': {'value':region_name},
                'bucket':{'value':bucket.bucket_name}
            },
            source = codebuild.Source.s3(
                bucket = bucket,
                path = 'pipeline/learner.zip'
            )
        )
        project.add_to_role_policy(
            iam.PolicyStatement(
                actions = ['athena:*'],
                resources = ['*']
            )
        )

        project.add_to_role_policy(
            iam.PolicyStatement(
                actions = ['iam:*'],
                resources = ['*']
            )
        )

        project.add_to_role_policy(
            iam.PolicyStatement(
                actions = ['glue:*'],
                resources = ['*']
            )
        )

        # Lambdas and Api GW
        api = agw.RestApi(self, "learner-api",
            rest_api_name="Learner Service",
            description="System to learn roles")    
        
        
        switcher = lambda_.Function(self,"Switcher",
            runtime = lambda_.Runtime.PYTHON_3_8,
            code =  lambda_.Code.from_asset("lambdas/switcher"),
            handler = "main.handler",
            
        )
        switcher.add_to_role_policy(iam.PolicyStatement(
            actions = ['iam:*'],
            resources = ['*']

        )
        )


        frontend = lambda_.Function(self,"Frontend",
            runtime = lambda_.Runtime.PYTHON_3_8,
            code =  lambda_.Code.from_asset("lambdas/frontend"),
            handler = "main.handler",
 
        )

        learner = lambda_.Function(self,"Learner",
            runtime = lambda_.Runtime.PYTHON_3_8,
            code =  lambda_.Code.from_asset("lambdas/learner"),
            handler = "main.handler",
            environment = {
                'codebuild':project.project_name,
                'region_name': region_name
            }
        )
        
        learner.add_to_role_policy(iam.PolicyStatement(
            actions = ['codebuild:StartBuild'],
            resources = [project.project_arn]

        )
        )

        get_switcher_integration = agw.LambdaIntegration(switcher,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        get_frontend_integration = agw.LambdaIntegration(frontend,
                request_templates={"application/json": '{ "statusCode": "200" }'})
        
        get_learner_integration = agw.LambdaIntegration(learner,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", get_frontend_integration) 
        
        switch = api.root.add_resource('switch')
        switch.add_method("GET",get_switcher_integration)

        learn = api.root.add_resource('learn')
        learn.add_method("GET",get_learner_integration)


        # Outputs
        core.CfnOutput(self,'BucketName',value=bucket.bucket_name)








    
        



