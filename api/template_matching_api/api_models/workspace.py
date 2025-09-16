from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .data_specification import DataSpecification


class WorkspaceBase(BaseModel):
    name: str

class WorkspaceIn(WorkspaceBase):
    data_specification: DataSpecification

class WorkspaceOut(WorkspaceBase):
    id: int
    data_specification: DataSpecification
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkspaceUpdate(BaseModel):
    name: str | None = None
    data_specification: DataSpecification | None = None
