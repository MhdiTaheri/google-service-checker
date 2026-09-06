from urllib.parse import urlparse

import requests

from config import REQUEST_TIMEOUT, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT, "Accept": "*/*"}

# Only read this many bytes of the body — we just need it for marker
# matching, not to download full pages.
BODY_SNIPPET_LIMIT = 20_000


def probe_url(url: str, timeout: float = REQUEST_TIMEOUT) -> dict:
    result = {
        "ok": False,
        "status_code": None,
        "final_url": None,
        "redirected": False,
        "redirected_to_other_domain": False,
        "elapsed_ms": None,
        "body_snippet": "",
        "error_type": None,
        "error_message": None,
    }

    original_domain = urlparse(url).netloc

    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
        )
        result["ok"] = True
        result["status_code"] = resp.status_code
        result["final_url"] = resp.url
        result["elapsed_ms"] = round(resp.elapsed.total_seconds() * 1000, 1)
        result["redirected"] = len(resp.history) > 0

        final_domain = urlparse(resp.url).netloc
        result["redirected_to_other_domain"] = (
            result["redirected"] and final_domain != original_domain
        )

        raw = resp.raw.read(BODY_SNIPPET_LIMIT, decode_content=True) or b""
        result["body_snippet"] = raw.decode("utf-8", errors="ignore").lower()
        resp.close()

    except requests.exceptions.SSLError as exc:
        result["error_type"] = "ssl"
        result["error_message"] = str(exc)
    except requests.exceptions.Timeout:
        result["error_type"] = "timeout"
        result["error_message"] = f"Request timed out after {timeout}s"
    except requests.exceptions.ConnectionError as exc:
        result["error_type"] = "connection"
        result["error_message"] = str(exc)
    except requests.RequestException as exc:
        result["error_type"] = "other"
        result["error_message"] = str(exc)

    return result
