from aws_cdk import (
    core,
    aws_apigateway as gw,
    aws_lambda as lambda_
)


class IamManagerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role_changer = lambda_.Function(self,"RoleChanger",
            runtime = lambda_.Runtime.PYTHON_3_8,
            code =  lambda_.Code.from_asset("lambdas/switcher"),
            handler = "main.handler",
        )

        # The code that defines your stack goes here
