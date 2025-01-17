#!/usr/bin/env python3

import aws_cdk as cdk
import os

from foundations import Foundations

# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")

if project_name:
    stack_name = f"{project_name}-{deployment_name}-{module_name}"
else:  # app.py not used in a seedfarmer context somehow
    stack_name = "sdlf-foundations"

app = cdk.App()
stack = cdk.Stack(app, stack_name)
Foundations(stack, "foundations")

app.synth()
