import json  # stdlib — resolves fine, see note above
from datetime import datetime, timezone


def build_report(ip_info: dict, results: list) -> dict:
    """Assemble the full JSON-serializable report dict."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "network": ip_info,
        "services": [
            {
                "name": r.display_name,
                "key": r.key,
                "url": r.url,
                "status": r.status,
                "confidence": r.confidence,
                "reason": r.reason,
                "dns": r.dns,
                "http": {
                    k: v for k, v in r.http.items() if k != "body_snippet"
                },
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "restricted": sum(
                1 for r in results if r.status in ("BLOCKED", "REGION_RESTRICTED", "CONNECTION_ERROR")
            ),
        },
    }


def write_report(ip_info: dict, results: list, path: str = "report.json") -> str:
    """Write the report to `path` and return the path."""
    report = build_report(ip_info, results)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path
