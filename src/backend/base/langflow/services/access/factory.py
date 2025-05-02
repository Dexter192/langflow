from __future__ import annotations

from typing import TYPE_CHECKING

from langflow.services.settings.service import SettingsService
from langflow.services.access.service import AccessService
from langflow.services.factory import ServiceFactory

if TYPE_CHECKING:
    from langflow.services.database.service import AccessService


class AccessServiceFactory(ServiceFactory):
    def __init__(self) -> None:
        super().__init__(AccessService)

    def create(self, settings_service: SettingsService):
        # Here you would have logic to create and configure a DatabaseService
        if not settings_service:
            msg = "No database"
            raise ValueError(msg)
        return AccessService(settings_service)
