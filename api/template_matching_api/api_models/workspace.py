from datetime import datetime
from pydantic import BaseModel, ConfigDict
from template_matching_api.api_models.data_specification import DataSpecification


class WorkspaceBase(BaseModel):
    name: str
    data_specification: DataSpecification

class WorkspaceIn(WorkspaceBase):
    pass


class WorkspaceOut(WorkspaceBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    data_specification: DataSpecification | None = None
