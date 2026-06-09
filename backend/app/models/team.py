from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # NBA team id
    abbreviation: Mapped[str] = mapped_column(String(5), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(50))
    nickname: Mapped[str] = mapped_column(String(50))
    conference: Mapped[str | None] = mapped_column(String(10), nullable=True)
    division: Mapped[str | None] = mapped_column(String(20), nullable=True)

    players: Mapped[list["Player"]] = relationship(back_populates="team")  # noqa: F821
