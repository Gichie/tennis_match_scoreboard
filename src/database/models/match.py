from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base

if TYPE_CHECKING:
    from src.database.models.player import Player


class Match(Base):
    __tablename__ = 'matches'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    player1_id: Mapped[int] = mapped_column(ForeignKey('players.id'), nullable=False)
    player2_id: Mapped[int] = mapped_column(ForeignKey('players.id'), nullable=False)
    winner_id: Mapped[int] = mapped_column(ForeignKey('players.id'), nullable=True)
    score: Mapped[dict] = mapped_column(JSON, nullable=True, default={})

    player1: Mapped["Player"] = relationship(foreign_keys=[player1_id], back_populates="matches_player1")
    player2: Mapped["Player"] = relationship(foreign_keys=[player2_id], back_populates="matches_player2")
    winner: Mapped["Player"] = relationship(foreign_keys=[winner_id], back_populates="matches_won")

    def __repr__(self):
        return f"<Match(id={self.id}, player1_id={self.player1_id}, player2_id={self.player2_id}, winner_id={self.winner_id})>"
