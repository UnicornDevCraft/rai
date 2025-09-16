import json
from datetime import datetime

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy import select, func
from sqlalchemy.orm import Session, sessionmaker

from template_matching_api.api.dependencies import get_session, get_session_maker
from template_matching_api.api_models.document_template import (
    DocumentTemplateOut,
    DocumentTemplateIn,
    DocumentTemplateUpdate,
)
from template_matching_api.db import session_scope
from template_matching_api.db_model import DocumentTemplate
from template_matching_api.file_storage import DocumentTemplateStorage

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def list_document_templates(
    session: Session = Depends(get_session),
) -> list[DocumentTemplateOut]:
    document_templates = session.scalars(select(DocumentTemplate))
    return [DocumentTemplateOut.model_validate(dt) for dt in document_templates]


@router.get("/{template_id}", status_code=status.HTTP_200_OK)
def get_document_template(
    template_id: int, session: Session = Depends(get_session)
) -> DocumentTemplateOut:
    template = session.scalar(
        select(DocumentTemplate).where(DocumentTemplate.id == template_id)
    )
    if template is None:
        raise HTTPException(status_code=404)
    return DocumentTemplateOut.model_validate(template)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_document_template(
    file: UploadFile = File(...),
    json_body: str = Form(...),
    session: Session = Depends(get_session),
) -> DocumentTemplateOut:
    body = json.loads(json_body)
    body["template_filename"] = file.filename
    body["template_file_type"] = file.headers.get("Content-Type", "image")
    body["uploaded_at"] = datetime.now()
    template = DocumentTemplate(**DocumentTemplateIn(**body).model_dump())
    session.add(template)
    session.flush()
    session.refresh(template)
    template_id = template.id
    template_storage = DocumentTemplateStorage()
    template_storage.save(template_id, file.file.read())
    return DocumentTemplateOut.model_validate(template)


@router.put("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_document_template(
    template_id: int,
    template_update: DocumentTemplateUpdate,
    session: Session = Depends(get_session),
) -> None:
    template = session.scalar(
        select(DocumentTemplate).where(DocumentTemplate.id == template_id)
    )
    if template is None:
        raise HTTPException(status_code=404)

    update_data = template_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(template, key):
            setattr(template, key, value)
    session.commit()


@router.post("/{template_id}/upload", status_code=status.HTTP_204_NO_CONTENT)
def upload_document_template(
    template_id: int, file: UploadFile, session: Session = Depends(get_session)
) -> None:
    template = session.scalar(
        select(DocumentTemplate).where(DocumentTemplate.id == template_id)
    )
    if template is None:
        raise HTTPException(status_code=404)
    if file.filename is None:
        raise ValueError("Cannot determine uploaded file filename")

    template.template_filename = file.filename
    template.template_file_type = file.headers.get("Content-Type", "image")
    template.uploaded_at = func.now()
    DocumentTemplateStorage().save(template_id, file.file.read())


@router.get("/{template_id}/download", status_code=status.HTTP_200_OK)
def download_document_template(
    template_id: int, session: Session = Depends(get_session)
) -> Response:
    try:
        filename, file_type = session.execute(
            select(
                DocumentTemplate.template_filename, DocumentTemplate.template_file_type
            ).where(DocumentTemplate.id == template_id)
        ).one()
        template_storage = DocumentTemplateStorage()
        file_bytes = template_storage.load(template_id)
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        return Response(content=file_bytes, media_type=file_type, headers=headers)
    except FileNotFoundError:
        raise HTTPException(status_code=404)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_template(
    template_id: int, session_maker: sessionmaker[Session] = Depends(get_session_maker)
) -> None:
    try:
        with session_scope(session_maker) as session:
            template = session.scalar(
                select(DocumentTemplate).where(DocumentTemplate.id == template_id)
            )
            if template is None:
                raise HTTPException(status_code=404)

            session.delete(template)
        DocumentTemplateStorage().delete(template_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404)
