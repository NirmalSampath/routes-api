from dotenv import load_dotenv
from aws_cdk import (
    Stack,
    BundlingOptions,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct
import os

load_dotenv()
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
                "DIGITRANSIT_API_KEY": os.getenv('DIGITRANSIT_API_KEY')
            }
        )

        api = apigw.LambdaRestApi(
            self, "ItineraryApi",
            handler=lambda_fn,
            deploy_options=apigw.StageOptions(
                tracing_enabled=True),
            proxy=False
        )

        routes = api.root.add_resource("routes")
        routes.add_method("GET", api_key_required=True)

        api_key = api.add_api_key("ApiKey")

        plan = api.add_usage_plan(
            "UsagePlan",
            name="ItineraryUsagePlan",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            )
        )

        plan.add_api_key(api_key)
        plan.add_api_stage(
            stage=api.deployment_stage
        )
