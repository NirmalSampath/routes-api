from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct
import os

class ItineraryStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        lambda_fn = _lambda.Function(
            self, "ItineraryHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset(os.path.join("src")),
            environment={"DIGITRANSIT_API_KEY": "your_api_key_here"}
        )

        api = apigw.LambdaRestApi(
            self, "ItineraryApi",
            handler=lambda_fn,
            proxy=False
        )

        items = api.root.add_resource("routes")
        items.add_method("GET")
