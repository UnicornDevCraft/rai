from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class FileType(StrEnum):
    PDF = "PDF"
    IMAGE = "IMAGE"


class SampleResult(BaseModel):
    sample_id: int
    score: float


class ExtendedSampleResult(SampleResult):
    created_at: datetime
    file_type: FileType
