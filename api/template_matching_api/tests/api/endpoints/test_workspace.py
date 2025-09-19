from datetime import datetime, timedelta, date

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient
from sqlalchemy import select

from template_matching_api.db_model import Workspace
from template_matching_api.api_models.workspace import WorkspaceOut


@pytest.fixture
def with_workspaces(session: Session) -> list[Workspace]:
    workspaces = []
    for idx in range(5):
        date_from = (datetime.now() - timedelta(days=7)).date() if idx % 2 == 0 else None
        date_to = datetime.now().date() if idx % 2 == 0 else None

        workspace = Workspace(
            name=f"workspace_{idx}",
            data_specification={
                "file_type": "PDF" if idx % 2 == 0 else "IMAGE",
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None
            }
        )
        workspaces.append(workspace)
    session.add_all(workspaces)
    session.commit()
    return workspaces


def test_list_workspaces(with_workspaces: list[Workspace], client: TestClient) -> None:
    resp = client.get("/api/workspace/")
    assert resp.status_code == 200
    resp_json = resp.json()
    assert len(resp_json) == len(with_workspaces)
    assert resp_json == [
        WorkspaceOut.model_validate(ws).model_dump(mode="json")
        for ws in with_workspaces
    ]


def test_get_workspace(with_workspaces: list[Workspace], client: TestClient) -> None:
    for ws in with_workspaces:
        resp = client.get(f"/api/workspace/{ws.id}")
        assert resp.status_code == 200
        assert resp.json() == WorkspaceOut.model_validate(ws).model_dump(mode="json")


def test_create_workspace(client: TestClient) -> None:
    date_from = (datetime.now() - timedelta(days=7)).date()
    date_to = datetime.now().date()
    data_specification = {
        "file_type": "IMAGE",
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
    }

    resp = client.post(
        "/api/workspace/",
        json={
            "name": "test_workspace",
            "data_specification": data_specification,
        }
    )
    assert resp.status_code == 201
    resp_json = resp.json()
    assert resp_json["name"] == "test_workspace"
    assert "id" in resp_json
    assert "created_at" in resp_json


def test_create_workspace_invalid_file_type(client: TestClient) -> None:
    resp = client.post(
        "/api/workspace/",
        json={
            "name": "bad_ws",
            "data_specification": {
                "file_type": "TXT",
                "date_from": "2024-01-01",
                "date_to": "2024-02-01",
            },
        },
    )
    assert resp.status_code == 422
    assert "file_type" in resp.json()["detail"][0]["loc"]


def test_create_workspace_invalid_dates(client: TestClient) -> None:
    resp = client.post(
        "/api/workspace/",
        json={
            "name": "bad_ws",
            "data_specification": {
                "file_type": "PDF",
                "date_from": "2100-01-01",
                "date_to": "2100-02-01",
            },
        },
    )
    assert resp.status_code == 422


def test_update_workspace(with_workspaces: list[Workspace], client: TestClient) -> None:
    ws = with_workspaces[0]

    new_name = "updated_workspace"
    new_spec = {
        "file_type": "PDF",
        "date_from": (datetime.now() - timedelta(days=3)).date().isoformat(),
        "date_to": datetime.now().date().isoformat(),
    }

    resp = client.patch(
        f"/api/workspace/{ws.id}",
        json={
            "name": new_name,
            "data_specification": new_spec,
        }
    )
    assert resp.status_code == 204

    resp_get = client.get(f"/api/workspace/{ws.id}")
    assert resp_get.status_code == 200
    resp_data = resp_get.json()
    assert resp_data["name"] == new_name
    assert resp_data["data_specification"] == new_spec


def test_partial_update_workspace_name_only(
    with_workspaces: list[Workspace], client: TestClient
) -> None:
    ws = with_workspaces[0]
    new_name = "only_name_updated"

    resp = client.patch(f"/api/workspace/{ws.id}", json={"name": new_name})
    assert resp.status_code == 204

    resp_get = client.get(f"/api/workspace/{ws.id}")
    assert resp_get.json()["name"] == new_name
    assert resp_get.json()["data_specification"] == ws.data_specification



def test_delete_workspace(with_workspaces: list[Workspace], client: TestClient, session: Session) -> None:
    ws = with_workspaces[0]
    resp = client.delete(f"/api/workspace/{ws.id}")
    assert resp.status_code == 204
    
    db_ws = session.scalar(select(Workspace).where(Workspace.id == ws.id))
    assert db_ws is None
