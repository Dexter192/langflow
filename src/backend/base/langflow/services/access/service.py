import casbin
from casbin.model import Model
from casbin_sqlalchemy_adapter import Adapter

from langflow.services.base import Service
from langflow.services.settings.service import SettingsService
from langflow.services.database.models.flow import Flow
from langflow.services.database.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import TYPE_CHECKING
from loguru import logger
if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

class AccessService(Service):
    name = "access_service"
    
    def __init__(self, settings_service: SettingsService):
        self.settings_service = settings_service

        if settings_service.settings.database_url is None:
            msg = "No database URL provided"
            raise ValueError(msg)
        self.database_url: str = settings_service.settings.database_url

        self.model = Model()
        self.model.load_model('src/backend/base/langflow/services/access/abac_model.conf')
        self.adapter = Adapter(self.database_url)
        self.enforcer = casbin.Enforcer(self.model, self.adapter)

    async def init_policy(self, session: AsyncSession):
        self.enforcer.clear_policy()
        if self.enforcer.get_policy():
            logger.debug("Casbin policy already migrated")
            return
        flows = (await session.exec(select(Flow))).all()
        users = (await session.exec(select(User))).all()
        
        # If the user_id of a flow or folder is the current userid, the user is the owner and should have read access
        self.enforcer.add_policy("r.sub.id == r.obj.user_id", "True", "edit")
        
        # Action hierarchy (admin > edit > view)
        # Editor is a subgroup of admin
        # self.enforcer.add_named_grouping_policy("g", "admin", "edit")
        # If someone is an editor, they can also view the flow -> Viewer is a subgroup of editor
        self.enforcer.add_named_grouping_policy("g", "edit", "view")

    
        # Other nice rules we can add
        # # Admin can do everything
        # self.enforcer.add_policy("r.sub.role == 'admin'", "True", "admin")
        # # Editor can edit folder 1
        # self.enforcer.add_policy("r.sub.role == 'editor'", "r.obj.folder_id == 'folder1'", "edit")
        # # Owner can edit their own flows
        # self.enforcer.add_policy("r.sub.username == r.obj.owner", "True", "edit")
        # # Teams can view all folders of their own team
        # self.enforcer.add_policy("r.sub.team == r.obj.team", "True", "view")



        # Folder-flow grouping: any permission given to 'folder1' should propagate to its flows unless the flow actively prohibits access
        # Flow 1, 2 and 3 are in folder 1. Permission to folder 1 gives access to flow 1-3
        # We probably want to add grouping policies for all flows in folders 
        # self.enforcer.add_named_grouping_policy("g", "folder1", "flow1")
        # self.enforcer.add_named_grouping_policy("g", "folder1", "flow2")
        # self.enforcer.add_named_grouping_policy("g", "folder1", "flow3")
        
        self.enforcer.save_policy()
