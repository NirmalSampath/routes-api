import requests
import os
from aws_lambda_powertools import Logger, Tracer
from .formatter import format_response, normalize_location
from utils.time_utils import format_time_int_to_iso

logger = Logger(service="digitransit-service")
tracer = Tracer(service="digitransit-service")

BASE_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
API_KEY = os.getenv("DIGITRANSIT_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "digitransit-subscription-key": API_KEY,
}

@tracer.capture_method
def get_stop_coords(location: str):
    """
    Fetch the latitude and longitude coordinates for a station by name.

    Args:
        location (str): Name of the station (e.g., "Helsinki", "Central Station").

    Returns:
        dict: Dictionary containing the stop's coordinates.
    """
    location = normalize_location(location)
    query = f"""
    {{
      stations(name: "{location}") {{
        gtfsId
        name
        lat
        lon
      }}
    }}"""

    resp = requests.post(BASE_URL, json={"query": query}, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()["data"]["stations"][0]
    logger.debug("Fetched stop coordinates", extra={"location": location, "coords": data})
    return {"lat": data["lat"], "long": data["lon"]}

@tracer.capture_method
def get_routes(start: str, stop: str, time: int):
    """
   Fetch transit routes between two stops at a given time using GraphQL Plan API.

   Args:
       start (str): Name of the origin station.
       stop (str): Name of the destination station.
       time (int): Desired latest arrival time in yyyymmddHHMMSS format.
                   Example: 20250909143000

   Returns:
       dict: Formatted response containing available routes
   """
    start_coords = get_stop_coords(start)
    stop_coords = get_stop_coords(stop)
    iso_time = format_time_int_to_iso(time)

    query = f"""
    {{
      planConnection(
        origin: {{location: {{coordinate: {{latitude: {start_coords["lat"]}, longitude: {start_coords["long"]}}}}}}}
        destination: {{location: {{coordinate: {{latitude: {stop_coords["lat"]}, longitude: {stop_coords["long"]}}}}}}}
        modes: {{transit: {{transit: [{{mode: BUS}}, {{mode: RAIL}}, {{mode: TRAM}}, {{mode: FERRY}}]}}}}
        dateTime: {{latestArrival: "{iso_time}"}}
      ) {{
        edges {{
          node {{
            start
            end
            legs {{
              mode
              from {{ name }}
              to {{ name }}
              trip {{ routeShortName }}
            }}
          }}
        }}
      }}
    }}
    """

    resp = requests.post(BASE_URL, json={"query": query}, headers=HEADERS)
    resp.raise_for_status()
    logger.debug("GraphQL response received")
    return format_response(resp.json())
