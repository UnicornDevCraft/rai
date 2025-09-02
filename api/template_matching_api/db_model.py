from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    template_filename: Mapped[str] = mapped_column(String, nullable=False)
    template_file_type: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    template_matching_job_templates: Mapped[list["TemplateMatchingJobTemplate"]] = (
        relationship(
            "TemplateMatchingJobTemplate",
            uselist=True,
            back_populates="document_template",
            passive_deletes=True,
        )
    )
    template_matching_jobs: Mapped[list["TemplateMatchingJob"]] = relationship(
        "TemplateMatchingJob",
        secondary="template_matching_job_templates",
        uselist=True,
        back_populates="document_templates",
    )


class TemplateMatchingJob(Base):
    __tablename__ = "template_matching_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    job_state: Mapped[str | None] = mapped_column(String, nullable=True)
    job_id: Mapped[str | None] = mapped_column(String, nullable=True)

    template_matching_job_templates: Mapped[list["TemplateMatchingJobTemplate"]] = (
        relationship(
            "TemplateMatchingJobTemplate",
            uselist=True,
            back_populates="template_matching_job",
            passive_deletes=True,
        )
    )
    document_templates: Mapped[list[DocumentTemplate]] = relationship(
        DocumentTemplate,
        secondary="template_matching_job_templates",
        uselist=True,
        back_populates="template_matching_jobs",
    )

    document_template_ids = association_proxy(
        "template_matching_job_templates",
        "document_template_id",
        creator=lambda template_id: TemplateMatchingJobTemplate(
            document_template_id=template_id
        ),
    )


class TemplateMatchingJobTemplate(Base):
    __tablename__ = "template_matching_job_templates"

    template_matching_job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("template_matching_jobs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_template_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("document_templates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    template_matching_job: Mapped[TemplateMatchingJob] = relationship(
        TemplateMatchingJob,
        uselist=False,
        back_populates="template_matching_job_templates",
    )
    document_template: Mapped[DocumentTemplate] = relationship(
        DocumentTemplate,
        uselist=False,
        back_populates="template_matching_job_templates",
    )
