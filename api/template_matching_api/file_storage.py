import os
from pathlib import Path

STORAGE_LOCATION = Path(os.path.realpath(__file__)).parents[1] / "storage"


class DocumentTemplateStorage:
    def __init__(self) -> None:
        # This is just to mimic storage like it would be on s3, where you just store bytes, so keeping the filename and file type in storage is not possible
        self.file_location = STORAGE_LOCATION / "templates"
        self.file_name = "template_file"

    def _get_location_for_template(self, template_id: int) -> Path:
        return self.file_location / str(template_id) / self.file_name

    def save(self, template_id: int, file_bytes: bytes) -> None:
        template_location=self._get_location_for_template(template_id)
        os.makedirs(os.path.dirname(template_location), exist_ok=True)
        template_location.write_bytes(file_bytes)

    def load(self, template_id: int) -> bytes:
        return self._get_location_for_template(template_id).read_bytes()

    def delete(self, template_id: int) -> None:
        self._get_location_for_template(template_id).unlink()
