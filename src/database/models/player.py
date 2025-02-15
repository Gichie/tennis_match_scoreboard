from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base


if TYPE_CHECKING:
    from src.database.models.match import Match

class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    matches_player1: Mapped[list["Match"]] = relationship(back_populates="player1", foreign_keys="[Match.player1_id]")
    matches_player2: Mapped[list["Match"]] = relationship(back_populates="player2", foreign_keys="[Match.player2_id]")
    matches_won: Mapped[list["Match"]] = relationship(back_populates="winner", foreign_keys="[Match.winner_id]")

    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name}')>"
