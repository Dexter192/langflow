from __future__ import annotations
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, Column
from typing import Optional
import enum
from sqlalchemy import Enum as SqlEnum, UniqueConstraint

class ItemTypeEnum(str, enum.Enum):
    flow = "flow"
    folder = "folder"


class TargetTypeEnum(str, enum.Enum):
    user = "user"


class AccessMapping(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "access_mapping"
    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)

    item_id: UUID = Field(index=True, nullable=False, foreign_key="flow.id")
    item_type: ItemTypeEnum = Field(sa_column=Column(SqlEnum(ItemTypeEnum)))

    target_id: UUID | None = Field(index=True, nullable=True, foreign_key="user.id")
    target_type: TargetTypeEnum = Field(sa_column=Column(SqlEnum(TargetTypeEnum)))


    __table_args__ = (
        UniqueConstraint("item_id", "target_id", name="unique_item_target_mapping"),
    )

class AccessMappingRead(SQLModel):
    id: UUID
    item_id: UUID
    item_type: ItemTypeEnum | None
    target_id: UUID | None
    target_type: TargetTypeEnum | None

class ShareItemRequest(AccessMapping):
    target_id: UUID | None = None
