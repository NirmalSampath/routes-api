# tests/test_formatter.py
import pytest
from services.formatter import format_response

def test_format_response_basic():
    sample_graphql = {
        "data": {
            "planConnection": {
                "edges": [
                    {
                        "node": {
                            "start": "2025-09-09T08:00:00+03:00",
                            "end": "2025-09-09T08:30:00+03:00",
                            "legs": [
                                {
                                    "mode": "WALK",
                                    "from": {"name": "Aalto Yliopisto"},
                                    "to": {"name": "Bus Stop 1"},
                                    "trip": None
                                },
                                {
                                    "mode": "BUS",
                                    "from": {"name": "Bus Stop 1"},
                                    "to": {"name": "Keilaniemi"},
                                    "trip": {"routeShortName": "550"}
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

    result = format_response(sample_graphql)
    assert isinstance(result, list)
    assert len(result) == 1

    route = result[0]
    assert route["start_time"] == 20250909080000
    assert route["end_time"] == 20250909083000
    assert len(route["legs"]) == 2

    first_leg = route["legs"][0]
    assert first_leg["mode"] == "WALK"
    assert first_leg["from"] == "Aalto Yliopisto"
    assert first_leg["to"] == "Bus Stop 1"
    assert first_leg["route_name"] == "N"

    second_leg = route["legs"][1]
    assert second_leg["mode"] == "BUS"
    assert second_leg["route_name"] == "550"

def test_format_response_handles_missing_fields():
    # missing legs or trip fields should be handled gracefully
    sample_graphql = {
        "data": {
            "planConnection": {
                "edges": [
                    {"node": {"start": None, "end": None, "legs": []}}
                ]
            }
        }
    }

    res = format_response(sample_graphql)
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["legs"] == []
