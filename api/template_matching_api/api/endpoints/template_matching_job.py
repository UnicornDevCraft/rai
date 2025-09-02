import random
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from template_matching_api.api.dependencies import get_session
from template_matching_api.api_models.sample import SampleResult
from template_matching_api.api_models.template_matching_job import (
    TemplateMatchingJobOut,
    TemplateMatchingJobIn,
    JobState,
    TemplateMatchingJobResults,
    TemplateMatchingJobTempLateResults,
)
from template_matching_api.db_model import TemplateMatchingJob

router = APIRouter()


def submit_job(job: TemplateMatchingJob) -> None:
    job.job_id = str(uuid.uuid4())
    job.job_state = random.choice(list(JobState))


def mock_job_results(job: TemplateMatchingJob) -> TemplateMatchingJobResults:
    template_ids = job.document_template_ids
    next_sample_id = 1
    template_results: list[TemplateMatchingJobTempLateResults] = []
    for template_id in template_ids:
        num_samples = random.randint(1, 100)
        sample_results: list[SampleResult] = []
        for _ in range(num_samples):
            sample_results.append(
                SampleResult(sample_id=next_sample_id, score=random.random())
            )
            next_sample_id += 1
        template_results.append(
            TemplateMatchingJobTempLateResults(
                template_id=template_id, sample_results=sample_results
            )
        )
    return TemplateMatchingJobResults(
        results_per_template=template_results,
        total_run_time=random.randint(1_000, 10_000),
    )


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

    return mock_job_results(job)


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
