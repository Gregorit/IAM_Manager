#!/usr/bin/env python3

from aws_cdk import core

from iam_manager.iam_manager_stack import IamManagerStack


app = core.App()
IamManagerStack(app, "iam-manager")

app.synth()
