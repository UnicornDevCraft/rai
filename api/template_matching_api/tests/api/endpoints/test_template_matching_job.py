import random
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from template_matching_api.api_models.template_matching_job import (
    JobState,
    TemplateMatchingJobOut,
    TemplateMatchingJobIn,
)
from .test_document_template import with_document_templates
from .test_workspace import with_workspaces
from template_matching_api.db_model import DocumentTemplate, TemplateMatchingJob, Workspace


@pytest.fixture
def with_template_matching_jobs(
    with_document_templates: list[DocumentTemplate], 
    with_workspaces: list[Workspace],
    session: Session
) -> list[TemplateMatchingJob]:
    jobs = []
    for idx, ws in enumerate(with_workspaces[:3]):
        job = TemplateMatchingJob(
            workspace_id=ws.id,
            job_id=str(uuid.uuid4()),
            job_state=random.choice(list(JobState)),
        )
        session.add(job)
        session.flush()

        job.document_templates=with_document_templates[: (idx + 1)]
        jobs.append(job)

    session.commit()
    return jobs


def test_list_template_matching_jobs(
    with_template_matching_jobs: list[TemplateMatchingJob], client: TestClient
) -> None:
    resp = client.get("/api/template-matching-job/")
    assert resp.status_code == 200

    resp_body = resp.json()
    assert resp_body == [
        TemplateMatchingJobOut.model_validate(job).model_dump(mode="json")
        for job in with_template_matching_jobs
    ]


def test_create_template_matching_job(
    with_document_templates: list[DocumentTemplate],
    with_workspaces: list[Workspace],
    client: TestClient
) -> None:
    template_ids = [template.id for template in with_document_templates[:2]]
    workspace_id = with_workspaces[0].id

    template_matching_job_in = TemplateMatchingJobIn(
        document_template_ids=template_ids,
        workspace_id=workspace_id
        )
    
    resp = client.post(
        "/api/template-matching-job/",
        json=template_matching_job_in.model_dump(mode="json"),
    )
    assert resp.status_code == 201

    resp_body = resp.json()
    assert resp_body["workspace"] is not None
    assert resp_body["workspace"]["id"] == workspace_id 
    assert [
        template["id"] for template in resp_body["document_templates"]
    ] == template_ids


def test_get_template_matching_job(
    with_template_matching_jobs: list[TemplateMatchingJob], client: TestClient
) -> None:
    for job in with_template_matching_jobs:
        resp = client.get(f"/api/template-matching-job/{job.id}")
        assert resp.status_code == 200
        assert resp.json() == TemplateMatchingJobOut.model_validate(job).model_dump(
            mode="json"
        )


def test_get_template_matching_job_results(
    with_template_matching_jobs: list[TemplateMatchingJob],
    with_workspaces: list[Workspace],
    client: TestClient,
    session: Session,
) -> None:
    for job in with_template_matching_jobs:
        job.workspace_id = with_workspaces[0].id
        job.job_state = JobState.SUCCEEDED
        session.commit()

        resp = client.get(f"/api/template-matching-job/{job.id}/results")
        assert resp.status_code == 200
        resp_body = resp.json()

        assert (
            {template_result["template_id"] for template_result in resp_body["results_per_template"]}
            == set(job.document_template_ids)
        )



def test_rerun_template_matching_job(
    with_template_matching_jobs: list[TemplateMatchingJob], client: TestClient
) -> None:
    for job in with_template_matching_jobs:
        resp = client.post(f"/api/template-matching-job/{job.id}/submit")
        assert resp.status_code == 204


def test_delete_template_matching_job(
    with_template_matching_jobs: list[TemplateMatchingJob],
    client: TestClient,
    session: Session,
) -> None:
    for job in with_template_matching_jobs:
        job_id = job.id
        assert job_id is not None

        resp = client.delete(f"/api/template-matching-job/{job_id}")
        assert resp.status_code == 204

        db_record = session.scalar(
            select(TemplateMatchingJob).where(TemplateMatchingJob.id == job_id)
        )
        assert db_record is None
