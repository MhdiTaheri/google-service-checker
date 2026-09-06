"""
Central configuration for Google Region Checker.

Every service is defined by:
- display_name : what gets printed to the user
- key           : internal identifier (used by services/*.py and JSON output)
- url           : the endpoint we actually probe
- expects_json  : if True, a JSON response is a strong "alive" signal
- block_markers : substrings that, if found in the response body, strongly
                  suggest a region / policy block page rather than a generic error
"""

REQUEST_TIMEOUT = 6  # seconds, per request
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 GoogleRegionChecker/1.0"
)

# Generic phrases Google (and similar providers) show on region-block pages.
DEFAULT_BLOCK_MARKERS = [
    "not available in your country",
    "not available in your region",
    "isn't available in your country",
    "is not available in your area",
    "country or region",
    "unsupported_country_region_territory",
    "restricted region",
]

SERVICES = [
    {
        "display_name": "Google Search",
        "key": "google_search",
        "url": "https://www.google.com/generate_204",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
    {
        "display_name": "Gmail",
        "key": "gmail",
        "url": "https://mail.google.com/mail/",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
    {
        "display_name": "Google Drive",
        "key": "drive",
        "url": "https://drive.google.com/",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
    {
        "display_name": "Gemini",
        "key": "gemini",
        "url": "https://gemini.google.com/",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
    {
        "display_name": "AI Studio",
        "key": "ai_studio",
        "url": "https://aistudio.google.com/",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
    {
        "display_name": "Gemini API",
        "key": "gemini_api",
        # Unauthenticated call: we only care about reachability, not auth.
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "expects_json": True,
        "block_markers": DEFAULT_BLOCK_MARKERS
        + ["user location is not supported", "failed_precondition"],
    },
    {
        "display_name": "YouTube",
        "key": "youtube",
        "url": "https://www.youtube.com/",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
    {
        "display_name": "Google Workspace",
        "key": "workspace",
        "url": "https://workspace.google.com/",
        "expects_json": False,
        "block_markers": DEFAULT_BLOCK_MARKERS,
    },
]

# Domains Google itself commonly redirects to as NORMAL behavior (login
# walls, consent screens, mobile app interstitials, etc). A redirect landing
# on one of these must NOT be treated as a block signal — e.g. Gmail/Drive/
# Workspace redirecting to accounts.google.com to ask you to sign in just
# means the service is reachable and working as intended.
TRUSTED_REDIRECT_SUFFIXES = [
    "google.com",
    "googleapis.com",
    "gstatic.com",
    "googleusercontent.com",
    "googlevideo.com",
    "youtube.com",
    "ytimg.com",
    "withgoogle.com",
]

# Phrases that show up on normal Google login/consent pages — NOT a region
# block, so they must never be added to a service's block_markers.
BENIGN_AUTH_MARKERS = [
    "sign in",
    "accounts.google.com",
    "choose an account",
    "verify it's you",
]

# Free, keyless geolocation API used to resolve the caller's public IP info.
IP_INFO_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,city,isp,org,as,query"
PUBLIC_IP_URL = "https://api.ipify.org?format=json"
