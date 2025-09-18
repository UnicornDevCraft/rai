from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from template_matching_api.api_models.document_template import DocumentTemplateOut
from template_matching_api.api_models.workspace import WorkspaceOut
from template_matching_api.api_models.sample import SampleResult, ExtendedSampleResult


class JobState(StrEnum):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


class TemplateMatchingJobIn(BaseModel):
    workspace_id: int | None
    document_template_ids: list[int]


class TemplateMatchingJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    job_state: JobState | None
    job_id: str | None

    workspace: WorkspaceOut | None
    document_templates: list[DocumentTemplateOut]


class TemplateMatchingJobTempLateResults(BaseModel):
    template_id: int
    sample_results: list[SampleResult] | list[ExtendedSampleResult]


class TemplateMatchingJobResults(BaseModel):
    results_per_template: list[TemplateMatchingJobTempLateResults]
    total_run_time: int
