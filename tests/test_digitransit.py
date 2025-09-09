# tests/test_digitransit.py
import os
import json
import types
import pytest

import services.digitransit as digitransit
from services import formatter

# A small fake response object to mimic requests.Response
class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = json.dumps(data)

    def json(self):
        return self._data

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}: {self.text}")

@pytest.fixture(autouse=True)
def set_api_key_env(monkeypatch):
    # Ensure DIGITRANSIT_API_KEY won't be empty for tests if code reads it
    monkeypatch.setenv("DIGITRANSIT_API_KEY", "test_key")
    yield

def test_get_routes_with_mocked_stop_coords_and_graphql(monkeypatch):
    """
    Test get_routes pipeline by:
    - mocking get_stop_coords() to return predictable coordinates
    - mocking requests.post to return a minimal planConnection response
    - asserting formatted output from get_routes is as expected
    """

    # 1) Mock get_stop_coords to avoid calling the upstream service
    def fake_get_stop_coords(name):
        if "Aalto" in name:
            return {"lat": 60.186, "long": 24.828}
        return {"lat": 60.180, "long": 24.820}

    monkeypatch.setattr(digitransit, "get_stop_coords", fake_get_stop_coords)

    # 2) Prepare a fake GraphQL response for planConnection
    graphql_response = {
        "data": {
            "planConnection": {
                "edges": [
                    {
                        "node": {
                            "start": "2025-09-09T08:20:00+03:00",
                            "end": "2025-09-09T08:40:00+03:00",
                            "walkDistance": 120,
                            "duration": 1200,
                            "legs": [
                                {
                                    "mode": "WALK",
                                    "from": {"name": "Aalto Yliopisto"},
                                    "to": {"name": "Otaniemi Metro"},
                                    "trip": None,
                                    "distance": 120
                                },
                                {
                                    "mode": "METRO",
                                    "from": {"name": "Otaniemi Metro"},
                                    "to": {"name": "Keilaniemi"},
                                    "trip": {"routeShortName": "M1"},
                                    "distance": 2000
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

    # 3) Mock requests.post inside digitransit module to return our fake response
    def fake_post(url, json=None, headers=None, timeout=None):
        # The digitransit.get_routes code calls requests.post only once for planConnection
        return FakeResponse(graphql_response, status_code=200)

    monkeypatch.setattr(digitransit, "requests", types.SimpleNamespace(post=fake_post))

    # 4) Call get_routes and validate output structure
    result = digitransit.get_routes("Aalto-Yliopisto", "Keilaniemi", 20250909084000)
    assert isinstance(result, list), "Expected a list of routes"
    assert len(result) == 1

    route = result[0]
    assert route["start_time"] == "2025-09-09T08:20:00+03:00"
    assert route["end_time"] == "2025-09-09T08:40:00+03:00"
    assert len(route["legs"]) == 2
    assert route["legs"][0]["mode"] == "WALK"
    assert route["legs"][1]["mode"] == "METRO"
    assert route["legs"][1]["route_name"] == "M1"

def test_get_stop_coords_handles_empty_result(monkeypatch):
    """
    Ensure get_stop_coords raises or returns gracefully when the stations array is empty.
    We'll mock requests.post to return an empty stations array and expect raise_for_status not triggered,
    but accessing [0] should raise IndexError which we assert.
    """
    empty_stations_resp = {"data": {"stations": []}}

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResponse(empty_stations_resp, status_code=200)

    monkeypatch.setattr(digitransit, "requests", types.SimpleNamespace(post=fake_post))
    with pytest.raises(IndexError):
        digitransit.get_stop_coords("Nonexistent Place")
