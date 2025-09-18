import random
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from template_matching_api.api.dependencies import get_session
from template_matching_api.api_models.template_matching_job import (
    TemplateMatchingJobOut,
    TemplateMatchingJobIn,
    JobState,
    TemplateMatchingJobResults,
)
from template_matching_api.db_model import TemplateMatchingJob, Workspace
from template_matching_api.api_models.data_specification import DataSpecification
from template_matching_api.jobs.template_matching_job import mock_job_results_with_data_spec

router = APIRouter()


def submit_job(job: TemplateMatchingJob) -> None:
    job.job_id = str(uuid.uuid4())
    job.job_state = random.choice(list(JobState))


@router.get("/", status_code=status.HTTP_200_OK)
def list_template_matching_jobs(
    session: Session = Depends(get_session),
) -> list[TemplateMatchingJobOut]:
    jobs = (
        session.scalars(
            select(TemplateMatchingJob).options(
                joinedload(TemplateMatchingJob.document_templates)
            )
        )
        .unique()
        .all()
    )
    return [TemplateMatchingJobOut.model_validate(job) for job in jobs]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_template_matching_job(
    template_matching_job_in: TemplateMatchingJobIn,
    session: Session = Depends(get_session),
) -> TemplateMatchingJobOut:
    if template_matching_job_in.workspace_id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    workspace = session.get(Workspace, template_matching_job_in.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    job = TemplateMatchingJob(**template_matching_job_in.model_dump())
    session.add(job)
    session.flush()
    session.refresh(job)
    submit_job(job)
    return TemplateMatchingJobOut.model_validate(job)


@router.get("/{template_matching_job_id}", status_code=status.HTTP_200_OK)
def get_template_matching_job(
    template_matching_job_id: int, session: Session = Depends(get_session)
) -> TemplateMatchingJobOut:
    job = session.scalar(
        select(TemplateMatchingJob).where(
            TemplateMatchingJob.id == template_matching_job_id
        )
    )
    if job is None:
        raise HTTPException(status_code=404)

    return TemplateMatchingJobOut.model_validate(job)


@router.get("/{template_matching_job_id}/results", status_code=status.HTTP_200_OK)
def get_template_matching_job_results(
    template_matching_job_id: int, session: Session = Depends(get_session)
) -> TemplateMatchingJobResults:
    job = session.scalar(
        select(TemplateMatchingJob).where(
            TemplateMatchingJob.id == template_matching_job_id
        )
    )
    if job is None or job.job_state != JobState.SUCCEEDED:
        raise HTTPException(status_code=404)

    data_spec_model = (
        DataSpecification.model_validate(job.workspace.data_specification)
        if job.workspace and job.workspace.data_specification
        else DataSpecification()
    )

    return mock_job_results_with_data_spec(job, data_spec_model)


@router.post(
    "/{template_matching_job_id}/submit", status_code=status.HTTP_204_NO_CONTENT
)
def rerun_template_matching_job(
    template_matching_job_id: int, session: Session = Depends(get_session)
) -> None:
    job = session.scalar(
        select(TemplateMatchingJob).where(
            TemplateMatchingJob.id == template_matching_job_id
        )
    )
    if job is None:
        raise HTTPException(status_code=404)

    submit_job(job)


@router.delete("/{template_matching_job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template_matching_job(
    template_matching_job_id: int, session: Session = Depends(get_session)
) -> None:
    job = session.scalar(
        select(TemplateMatchingJob).where(
            TemplateMatchingJob.id == template_matching_job_id
        )
    )
    if job is None:
        raise HTTPException(status_code=404)

    session.delete(job)
