import json
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from services.digitransit import get_routes

# Initialize Powertools
logger = Logger(service="itinerary-api")
tracer = Tracer(service="itinerary-api")
metrics = Metrics(namespace="AndreaItinerary", service="routes")

@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event, context):
    """
    Lambda handler for API Gateway.
    Expects query params: start, stop, time (yyyymmddHHMMSS)
    """
    logger.info("Incoming request", extra={"event": event})

    try:
        params = event.get("queryStringParameters", {}) or {}
        start = params.get("start")
        stop = params.get("stop")
        time = params.get("time")

        if not all([start, stop, time]):
            logger.warning("Missing parameters", extra={"params": params})
            metrics.add_metric("BadRequest", unit=MetricUnit.Count, value=1)
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required parameters"})
            }

        routes = get_routes(start, stop, int(time))
        logger.info("Routes fetched", extra={"count": len(routes)})

        metrics.add_metric("ItineraryQuerySuccess", unit=MetricUnit.Count, value=1)

        return {
            "statusCode": 200,
            "body": json.dumps(routes)
        }

    except Exception as e:
        logger.exception(f"Error fetching routes: {str(e)}")
        metrics.add_metric("ItineraryQueryFailure", unit=MetricUnit.Count, value=1)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
