
from services.base import ServiceResult, check_service
from services.registry import get_service_config


def check() -> ServiceResult:
    return check_service(get_service_config("workspace"))
