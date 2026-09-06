import requests

from config import IP_INFO_URL, PUBLIC_IP_URL, REQUEST_TIMEOUT, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT}


def get_public_ip() -> str | None:
    """Return the caller's public IPv4/IPv6 address, or None on failure."""
    try:
        resp = requests.get(PUBLIC_IP_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json().get("ip")
    except (requests.RequestException, ValueError):
        return None


def get_geo_info(ip: str | None) -> dict:
    fallback = {
        "ip": ip or "Unknown",
        "country": "Unknown",
        "country_code": "Unknown",
        "city": "Unknown",
        "isp": "Unknown",
        "org": "Unknown",
        "asn": "Unknown",
    }

    if not ip:
        return fallback

    try:
        url = IP_INFO_URL.format(ip=ip)
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "success":
            return fallback

        return {
            "ip": ip,
            "country": data.get("country", "Unknown"),
            "country_code": data.get("countryCode", "Unknown"),
            "city": data.get("city", "Unknown"),
            "isp": data.get("isp", "Unknown"),
            "org": data.get("org", "Unknown"),
            "asn": data.get("as", "Unknown"),
        }
    except (requests.RequestException, ValueError):
        return fallback


def get_ip_report() -> dict:
    """Convenience wrapper: fetch public IP and its geo info in one call."""
    ip = get_public_ip()
    return get_geo_info(ip)
