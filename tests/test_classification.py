
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.base import (  # noqa: E402
    STATUS_AVAILABLE,
    STATUS_BLOCKED,
    STATUS_CONNECTION_ERROR,
    STATUS_REGION_RESTRICTED,
    STATUS_UNKNOWN,
    _classify,
)

BLOCK_MARKERS = ["not available in your country"]


def _dns(resolved=True, error=None):
    return {"hostname": "example.com", "resolved": resolved, "addresses": ["1.2.3.4"] if resolved else [], "error": error}


def _http(**overrides):
    base = {
        "ok": True,
        "status_code": 200,
        "final_url": "https://example.com/",
        "redirected": False,
        "redirected_to_other_domain": False,
        "elapsed_ms": 120.0,
        "body_snippet": "",
        "error_type": None,
        "error_message": None,
    }
    base.update(overrides)
    return base


def test_dns_failure_is_blocked():
    status, _, _ = _classify(_dns(resolved=False, error="NXDOMAIN"), _http(), BLOCK_MARKERS)
    assert status == STATUS_BLOCKED


def test_connection_error_is_blocked():
    status, _, _ = _classify(_dns(), _http(ok=False, error_type="connection"), BLOCK_MARKERS)
    assert status == STATUS_BLOCKED


def test_timeout_is_connection_error():
    status, _, _ = _classify(_dns(), _http(ok=False, error_type="timeout"), BLOCK_MARKERS)
    assert status == STATUS_CONNECTION_ERROR


def test_region_block_marker_in_body():
    status, _, _ = _classify(
        _dns(),
        _http(status_code=403, body_snippet="this service is not available in your country"),
        BLOCK_MARKERS,
    )
    assert status == STATUS_REGION_RESTRICTED


def test_redirect_to_unrelated_domain_is_blocked():
    status, _, _ = _classify(
        _dns(),
        _http(redirected=True, redirected_to_other_domain=True, final_url="https://isp-block-page.local/"),
        BLOCK_MARKERS,
    )
    assert status == STATUS_BLOCKED


def test_redirect_to_google_signin_is_available():
    # e.g. Gmail/Drive/Workspace redirecting to accounts.google.com to log in
    # is normal behavior and must NOT be treated as blocked.
    status, _, _ = _classify(
        _dns(),
        _http(
            status_code=200,
            redirected=True,
            redirected_to_other_domain=True,
            final_url="https://accounts.google.com/ServiceLogin?service=mail",
        ),
        BLOCK_MARKERS,
    )
    assert status == STATUS_AVAILABLE


def test_normal_200_is_available():
    status, _, _ = _classify(_dns(), _http(status_code=200), BLOCK_MARKERS)
    assert status == STATUS_AVAILABLE


def test_plain_404_is_still_available():
    status, _, _ = _classify(_dns(), _http(status_code=404), BLOCK_MARKERS)
    assert status == STATUS_AVAILABLE


def test_server_error_is_unknown():
    status, _, _ = _classify(_dns(), _http(status_code=503), BLOCK_MARKERS)
    assert status == STATUS_UNKNOWN


if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed = 0
    for t in tests:
        t()
        passed += 1
        print(f"OK  {t.__name__}")
    print(f"\n{passed}/{len(tests)} tests passed")
