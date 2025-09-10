from datetime import datetime, timezone, timedelta

def format_time_int_to_iso(dt_int: int, tz_offset: int = 3) -> str:
    """
    Convert datetime in yyyymmddHHMMSS (int) to ISO 8601 with timezone.
    Example: 20250909143003 -> "2025-09-09T14:30+03:00"
    """
    dt_str = str(dt_int)
    dt = datetime.strptime(dt_str, "%Y%m%d%H%M%S")
    dt = dt.replace(tzinfo=timezone(timedelta(hours=tz_offset)))
    formatted = dt.strftime("%Y-%m-%dT%H:%M%z")
    return formatted[:-2] + ":" + formatted[-2:]


def format_iso_to_time_int(iso_str: str) -> int | None:
    """
    Convert ISO 8601 datetime with timezone into yyyymmddHHMMSS (int).
    Example: "2025-09-09T14:30+03:00" -> 20250909143000
    Returns None if iso_str is None or invalid.
    """
    if not iso_str:
        return None

    try:
        # Parse ISO string into datetime
        dt = datetime.fromisoformat(iso_str)
        # Format back to yyyymmddHHMMSS
        return int(dt.strftime("%Y%m%d%H%M%S"))
    except ValueError:
        return None