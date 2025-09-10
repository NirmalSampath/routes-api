from aws_cdk import (
    Stack,
    BundlingOptions,
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
        code=_lambda.Code.from_asset(
            path=os.path.join("src"),
            bundling=BundlingOptions(
                image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                command=[
                    "bash", "-c",
                    "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                ],
            )
        ),
        environment={
            "DIGITRANSIT_API_KEY": "give_you_api_key"
        }
    )

        api = apigw.LambdaRestApi(
            self, "ItineraryApi",
            handler=lambda_fn,
            proxy=False
        )

        items = api.root.add_resource("routes")
        items.add_method("GET")