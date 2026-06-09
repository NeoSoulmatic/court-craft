from datetime import date

from sqlalchemy import Date, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("dedup_key", name="uq_transaction_dedup"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dedup_key: Mapped[str] = mapped_column(String(64), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    season: Mapped[str] = mapped_column(String(10), index=True)  # e.g. 2024-25
    transaction_type: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), default="basketball-reference")
