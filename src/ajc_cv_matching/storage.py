from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Float, Integer, String, create_engine, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(32), default="cv")
    processed_at: Mapped[str] = mapped_column(String(40))


class MatchRecord(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(128), index=True)
    pathway_id: Mapped[str] = mapped_column(String(128), index=True)
    boolean_score: Mapped[float] = mapped_column(Float)
    weighted_score: Mapped[float] = mapped_column(Float)
    matched_tokens: Mapped[str] = mapped_column(String)
    missing_tokens: Mapped[str] = mapped_column(String)


class AuditStore:
    """Small SQLite audit store mirroring the local persistence principle of the V1."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(self.engine)

    def replace_document_results(self, document_id: str, rows: list[dict[str, object]]) -> None:
        with Session(self.engine) as session:
            existing = session.query(DocumentRecord).filter_by(document_id=document_id).one_or_none()
            now = datetime.now(timezone.utc).isoformat()
            if existing is None:
                session.add(DocumentRecord(document_id=document_id, source_type="cv", processed_at=now))
            else:
                existing.processed_at = now

            session.execute(delete(MatchRecord).where(MatchRecord.document_id == document_id))
            for row in rows:
                session.add(
                    MatchRecord(
                        document_id=document_id,
                        pathway_id=str(row["pathway_id"]),
                        boolean_score=float(row["boolean_score"]),
                        weighted_score=float(row["weighted_score"]),
                        matched_tokens=str(row["matched_tokens"]),
                        missing_tokens=str(row["missing_tokens"]),
                    )
                )
            session.commit()
