
from config import SERVICES
from services.base import ServiceResult, check_service


def run_all_checks(progress_callback=None) -> list[ServiceResult]:
    """
    Run every configured service check in order.

    progress_callback(service_display_name: str) is called right before each
    service is checked, so a CLI can print "Checking Gmail..." live instead
    of waiting for everything to finish.
    """
    results = []
    for service_config in SERVICES:
        if progress_callback:
            progress_callback(service_config["display_name"])
        results.append(check_service(service_config))
    return results
