from services.base import (
    STATUS_AVAILABLE,
    STATUS_BLOCKED,
    STATUS_CONNECTION_ERROR,
    STATUS_REGION_RESTRICTED,
    STATUS_UNKNOWN,
)

# ANSI colors — disabled automatically by NO_COLOR env var or on dumb terminals
# is out of scope for this simple tool, but kept easy to strip if needed.
class C:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


STATUS_ICON = {
    STATUS_AVAILABLE: (f"{C.GREEN}✓{C.RESET}", f"{C.GREEN}AVAILABLE{C.RESET}"),
    STATUS_BLOCKED: (f"{C.RED}✗{C.RESET}", f"{C.RED}BLOCKED{C.RESET}"),
    STATUS_REGION_RESTRICTED: (f"{C.RED}✗{C.RESET}", f"{C.RED}RESTRICTED{C.RESET}"),
    STATUS_CONNECTION_ERROR: (f"{C.YELLOW}!{C.RESET}", f"{C.YELLOW}CONN_ERROR{C.RESET}"),
    STATUS_UNKNOWN: (f"{C.YELLOW}?{C.RESET}", f"{C.YELLOW}UNKNOWN{C.RESET}"),
}


def print_banner():
    print(f"{C.CYAN}{C.BOLD}")
    print("╔══════════════════════════════════════╗")
    print("║        Google Region Checker          ║")
    print("╚══════════════════════════════════════╝")
    print(C.RESET)


def print_ip_report(ip_info: dict):
    print(f"🌐 Public IP: {ip_info['ip']}")
    print(f"📍 Country:   {ip_info['country']} ({ip_info['country_code']})")
    print(f"🏙️  City:      {ip_info['city']}")
    print(f"🏢 ISP:       {ip_info['isp']}")
    print()


def print_checking(display_name: str):
    print(f"{C.DIM}Checking {display_name}...{C.RESET}", end="\r")


def print_result_line(result):
    icon, label = STATUS_ICON.get(result.status, ("?", result.status))
    name_col = result.display_name.ljust(20)
    # pad label visually since it contains ANSI codes
    print(f"{icon} {name_col} {label}")


def print_results(results):
    print("Checking Google services...\n")
    for result in results:
        print_result_line(result)
    print()


def print_summary(results):
    blocked_like = [
        r
        for r in results
        if r.status in (STATUS_BLOCKED, STATUS_REGION_RESTRICTED, STATUS_CONNECTION_ERROR)
    ]
    total = len(results)
    n_blocked = len(blocked_like)

    print("──────────────────────────────────────")
    print(f"{C.BOLD}Summary{C.RESET}")
    print("──────────────────────────────────────\n")
    print(f"Restricted services: {n_blocked}/{total}\n")

    if not blocked_like:
        print(f"{C.GREEN}All checked services appear reachable from this network.{C.RESET}")
        return

    region_restricted = [r for r in blocked_like if r.status == STATUS_REGION_RESTRICTED]
    hard_blocked = [r for r in blocked_like if r.status == STATUS_BLOCKED]

    if region_restricted and not hard_blocked:
        reason = "🌍 Regional availability / provider policy"
    elif hard_blocked and not region_restricted:
        reason = "🚫 Network-level blocking (DNS/IP/TLS filtering)"
    else:
        reason = "🌍🚫 Mix of regional policy and network-level blocking"

    avg_confidence = round(sum(r.confidence for r in blocked_like) / len(blocked_like))

    print(f"Possible reason:\n{reason}\n")
    print(f"Confidence: {avg_confidence}%\n")

    print(f"{C.DIM}Details:{C.RESET}")
    for r in blocked_like:
        print(f"  {C.DIM}- {r.display_name}: {r.reason}{C.RESET}")
    print()
