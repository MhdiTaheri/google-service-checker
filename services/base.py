
from dataclasses import dataclass, field
from urllib.parse import urlparse

from config import TRUSTED_REDIRECT_SUFFIXES
from network.dns import resolve_hostname
from network.http import probe_url

STATUS_AVAILABLE = "AVAILABLE"
STATUS_BLOCKED = "BLOCKED"
STATUS_REGION_RESTRICTED = "REGION_RESTRICTED"
STATUS_CONNECTION_ERROR = "CONNECTION_ERROR"
STATUS_UNKNOWN = "UNKNOWN"


@dataclass
class ServiceResult:
    display_name: str
    key: str
    url: str
    status: str
    confidence: int  # 0-100
    reason: str
    dns: dict = field(default_factory=dict)
    http: dict = field(default_factory=dict)

    def is_available(self) -> bool:
        return self.status == STATUS_AVAILABLE


def _is_trusted_domain(hostname: str | None) -> bool:
    """True if `hostname` is Google's own infrastructure (login pages,
    CDN, consent screens, etc.) — a redirect landing here is NORMAL,
    not a sign of blocking."""
    if not hostname:
        return False
    hostname = hostname.lower()
    return any(hostname == suffix or hostname.endswith("." + suffix) for suffix in TRUSTED_REDIRECT_SUFFIXES)


def _classify(dns_info: dict, http_info: dict, block_markers: list[str]) -> tuple[str, int, str]:
    """
    Turn raw DNS + HTTP signals into (status, confidence, human_reason).

    The logic is deliberately layered, cheapest/most-reliable signal first:
      1. DNS failure            -> almost certainly BLOCKED (censorship-style)
      2. Connection-level error -> BLOCKED (firewall reset/drop) unless it
         looks like a generic outage (very low confidence UNKNOWN instead)
      3. TLS/SSL error          -> BLOCKED (common with SNI-based filtering)
      4. Response body contains a region-block marker -> REGION_RESTRICTED
      5. Redirect landed on a different domain entirely -> BLOCKED
         (classic sign of a captive/ISP block page)
      6. HTTP 2xx/3xx/normal 4xx from the real service -> AVAILABLE
      7. Anything else -> UNKNOWN
    """
    # 1. DNS-level blocking
    if not dns_info.get("resolved", False):
        return (
            STATUS_BLOCKED,
            80,
            "DNS resolution failed — often a sign of DNS-level filtering.",
        )

    # 2 & 3. Connection / TLS failures
    error_type = http_info.get("error_type")
    if error_type == "connection":
        return (
            STATUS_BLOCKED,
            70,
            "Connection was refused/reset — consistent with IP-level blocking.",
        )
    if error_type == "ssl":
        return (
            STATUS_BLOCKED,
            65,
            "TLS handshake failed — consistent with SNI-based filtering.",
        )
    if error_type == "timeout":
        return (
            STATUS_CONNECTION_ERROR,
            50,
            "Connection timed out — could be blocking or an unrelated network issue.",
        )
    if error_type == "other" or not http_info.get("ok", False):
        return (
            STATUS_UNKNOWN,
            30,
            "Request failed for an undetermined reason.",
        )

    body = http_info.get("body_snippet", "")
    status_code = http_info.get("status_code")

    # 4. Explicit region-block marker in the body
    for marker in block_markers:
        if marker in body:
            return (
                STATUS_REGION_RESTRICTED,
                90,
                f"Response body matched a known block phrase ('{marker}').",
            )

    # 5. Redirected somewhere that isn't the service itself.
    # A redirect to Google's own login/consent/CDN domains (e.g. Gmail or
    # Drive sending you to accounts.google.com to sign in) is NORMAL and
    # actually proves the service is reachable — only a redirect to some
    # unrelated third-party domain (an ISP block page, a captive portal)
    # counts as a block signal.
    if http_info.get("redirected_to_other_domain"):
        final_domain = urlparse(http_info.get("final_url") or "").hostname
        if not _is_trusted_domain(final_domain):
            return (
                STATUS_BLOCKED,
                60,
                f"Redirected away to an unrelated domain ({http_info.get('final_url')}).",
            )
        # else: trusted Google domain (e.g. a sign-in wall) — fall through
        # to the normal status-code handling below.

    # 6. Plain HTTP outcome
    if status_code is not None and 200 <= status_code < 400:
        return (STATUS_AVAILABLE, 90, f"Reachable, HTTP {status_code}.")

    if status_code == 403:
        return (
            STATUS_REGION_RESTRICTED,
            55,
            "HTTP 403 — could be a region block or an unauthenticated API call.",
        )

    if status_code is not None and 400 <= status_code < 500:
        # Reached the real server and got a "normal" client error (e.g. 404
        # on a probe endpoint) — the service itself is reachable.
        return (
            STATUS_AVAILABLE,
            65,
            f"Reachable, HTTP {status_code} (server responded normally).",
        )

    if status_code is not None and status_code >= 500:
        return (
            STATUS_UNKNOWN,
            35,
            f"Server error (HTTP {status_code}) — inconclusive.",
        )

    return (STATUS_UNKNOWN, 20, "Could not determine a clear status.")


def check_service(service_config: dict) -> ServiceResult:
    """Run the full DNS + HTTP pipeline for one service config entry."""
    url = service_config["url"]
    block_markers = service_config.get("block_markers", [])

    dns_info = resolve_hostname(url)
    http_info = probe_url(url) if dns_info.get("resolved") else {
        "ok": False,
        "status_code": None,
        "final_url": None,
        "redirected": False,
        "redirected_to_other_domain": False,
        "elapsed_ms": None,
        "body_snippet": "",
        "error_type": "dns",
        "error_message": dns_info.get("error"),
    }

    status, confidence, reason = _classify(dns_info, http_info, block_markers)

    return ServiceResult(
        display_name=service_config["display_name"],
        key=service_config["key"],
        url=url,
        status=status,
        confidence=confidence,
        reason=reason,
        dns=dns_info,
        http=http_info,
    )
