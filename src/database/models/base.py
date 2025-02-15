from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Автоимпорт моделей, чтобы Alembic не требовал явного импорта в env.py
from src.database.models import player, match  # noqa
