"""Municipal Reference Database Models.

Architectural and Security Rationale:
- Defines the read-only schema for querying authoritative civil registry records.
- Used strictly for reference lookups and cross-verification against OCR-extracted fields.
- Zero citizen data modifications are permitted through this model layer.
- All column names and relationship attributes follow strict snake_case conventions.
"""

from datetime import date
from typing import Optional
from sqlalchemy import Boolean, Date, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for municipal database models."""
    pass


class MunicipalCitizenRecord(Base):
    """Authoritative municipal citizen reference record."""

    __tablename__ = "municipal_citizen_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    national_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    certificate_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    full_name_km: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    district_office: Mapped[str] = mapped_column(String(255), nullable=False)
    commune: Mapped[str] = mapped_column(String(255), nullable=False)
    province: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_citizen_id_cert", "national_id", "certificate_no"),
        Index("idx_citizen_name_km", "full_name_km"),
        Index("idx_citizen_name_en", "full_name_en"),
    )

    def to_dict(self) -> dict:
        """Serializes reference entity to snake_case dictionary."""
        return {
            "national_id": self.national_id,
            "certificate_no": self.certificate_no,
            "full_name_km": self.full_name_km,
            "full_name_en": self.full_name_en,
            "gender": self.gender,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "district_office": self.district_office,
            "commune": self.commune,
            "province": self.province,
            "is_active": self.is_active,
        }
