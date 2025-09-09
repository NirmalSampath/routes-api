from src.utils.time_utils import format_iso_to_time_int
import re

def format_response(response: dict) -> list:
    """
    Format a raw GraphQL planConnection response into a simplified list of routes.
    """
    routes = response.get("data", {}).get("planConnection", {}).get("edges", [])
    suggested_routes = []

    for edge in routes:
        node = edge.get("node", {})
        suggested_route = {
            "start_time": format_iso_to_time_int(node.get("start")),
            "end_time": format_iso_to_time_int(node.get("end")),
            "legs": []
        }

        for leg in node.get("legs", []):
            suggested_leg = {
                "mode": leg.get("mode", "UNKNOWN"),
                "from": leg.get("from", {}).get("name", "N/A"),
                "to": leg.get("to", {}).get("name", "N/A"),
                "route_name": leg.get("trip").get("routeShortName", "N/A") if leg.get("trip") else "N",
            }
            suggested_route["legs"].append(suggested_leg)

        suggested_routes.append(suggested_route)
    return suggested_routes


def normalize_location(location: str) -> str:
    """
    Normalize location name for GraphQL queries:
    - Trim leading/trailing spaces
    - Collapse internal whitespace into single '-'

    Example:
        " central station  " -> "central-station"
    """
    cleaned = location.strip()
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned