
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from template_matching_api.api.dependencies import get_session
from template_matching_api.api_models.workspace import (
    WorkspaceIn,
    WorkspaceOut,
    WorkspaceUpdate
)
from template_matching_api.db_model import Workspace


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def list_workspaces(
    session: Session = Depends(get_session),
) -> list[WorkspaceOut]:
    workspaces = session.scalars(select(Workspace))
    return [WorkspaceOut.model_validate(ws) for ws in workspaces]


@router.get("/{workspace_id}", status_code=status.HTTP_200_OK)
def get_workspace(
    workspace_id: int, session: Session = Depends(get_session)
) -> WorkspaceOut:
    workspace = session.scalar(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceOut.model_validate(workspace)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace_in: WorkspaceIn,
    session: Session = Depends(get_session),
    ) -> WorkspaceOut:
    workspace = Workspace(
        name=workspace_in.name,
        data_specification=workspace_in.data_specification.model_dump(mode="json")
    )
    session.add(workspace)
    session.flush()
    return WorkspaceOut.model_validate(workspace)


@router.patch("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_workspace(
    workspace_id: int,
    update: WorkspaceUpdate,
    session: Session = Depends(get_session),
    ) -> None:
    workspace = session.scalar(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    if update.name is not None:
        workspace.name = update.name
    if update.data_specification is not None:
        workspace.data_specification = update.data_specification.model_dump(mode="json")


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: int, session: Session = Depends(get_session)) -> None:
    workspace = session.scalar(select(Workspace).where(Workspace.id == workspace_id))
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    session.delete(workspace)

