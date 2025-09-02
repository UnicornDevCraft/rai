import random
from datetime import date, timedelta
from typing import Any

from template_matching_api.api_models.template_matching_job import (
    TemplateMatchingJobResults,
    TemplateMatchingJobTempLateResults,
)
from template_matching_api.api_models.sample import (
    FileType,
    SampleResult,
    ExtendedSampleResult,
)
from template_matching_api.db_model import TemplateMatchingJob


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


def mock_job_results_with_data_spec(
    job: TemplateMatchingJob, data_specification: dict[str, Any]
) -> TemplateMatchingJobResults:
    # This would normally accept Pydantic model with data specification instead of plain dict, but I did not want to prepare the model for the task
    template_ids = job.document_template_ids
    next_sample_id = 1
    template_results: list[TemplateMatchingJobTempLateResults] = []

    available_file_types: list[FileType] = (
        [FileType[data_specification["file_type"]]]
        if "file_type" in data_specification
        else list(FileType)
    )
    date_from = (
        data_specification["date_from"]
        if "date_from" in data_specification
        else date.today()
    )
    date_to = (
        data_specification["date_to"]
        if "date_to" in data_specification
        else date.today()
    )
    num_days = (date_to - date_from + timedelta(days=1)).days
    available_dates = [date_from + timedelta(days=day) for day in range(num_days)]
    for template_id in template_ids:
        num_samples = random.randint(1, 100)
        sample_results: list[SampleResult] = []
        for _ in range(num_samples):
            sample_results.append(
                ExtendedSampleResult(
                    sample_id=next_sample_id,
                    score=random.random(),
                    file_type=random.choice(available_file_types),
                    created_at=random.choice(available_dates),
                )
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
