from aws_cdk import (
    core,
    aws_apigateway as agw,
    aws_lambda as lambda_,
    aws_cloudtrail as cloudtrail
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
        tail = cloudtrail.Trail(self,'CloudTrail')



