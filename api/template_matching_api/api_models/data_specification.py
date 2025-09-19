from typing_extensions import Self

from datetime import date
from pydantic import BaseModel, field_validator, model_validator

from template_matching_api.api_models.sample import FileType


class DataSpecification(BaseModel):
    file_type: FileType | None = None
    date_from: date | None = None
    date_to: date | None = None

    @field_validator("date_from", "date_to")
    def date_in_present(cls, v: date) -> date:
        if v and v > date.today():
            raise ValueError("Dates cannot be in the future")
        return v
    
    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be <= date_to")
        return self
