#!/usr/bin/env python3

from aws_cdk import core

from iam_manager.iam_manager_stack import IamManagerStack

import configparser


# Read Config File
config = configparser.ConfigParser()
config.read('config.ini')

app_envs = {
    'env':core.Environment(
        account=config.get('MAIN','account_id'),
        region=config.get('MAIN','region')
    ),
    'region_name' : config.get('MAIN','region')
}

app = core.App()
IamManagerStack(app, "iam-manager",**app_envs)

app.synth()
