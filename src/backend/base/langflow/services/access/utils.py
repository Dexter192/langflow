from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from langflow.services.access.service import AccessService

def initialize_access_model(*kwargs) -> None:
    logger.debug("Initializing Casbin ruleset")
    from langflow.services.deps import get_access_service

    access_service: AccessService = get_access_service()
    # access_service.init_policy()
    
