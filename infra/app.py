#!/usr/bin/env python3
import aws_cdk as cdk
from stack import ItineraryStack

app = cdk.App()
ItineraryStack(app, "ItineraryStack")
app.synth()
