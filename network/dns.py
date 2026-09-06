import socket
from urllib.parse import urlparse


def resolve_hostname(url: str, timeout: float = 5.0) -> dict:
    hostname = urlparse(url).hostname or url
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)

    result = {"hostname": hostname, "resolved": False, "addresses": [], "error": None}

    try:
        infos = socket.getaddrinfo(hostname, None)
        addresses = sorted({info[4][0] for info in infos})
        result["resolved"] = len(addresses) > 0
        result["addresses"] = addresses
    except socket.gaierror as exc:
        result["error"] = f"DNS resolution failed: {exc}"
    except socket.timeout:
        result["error"] = "DNS resolution timed out"
    finally:
        socket.setdefaulttimeout(old_timeout)

    return result
