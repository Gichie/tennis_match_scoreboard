import json
import uuid

from sqlalchemy.orm import joinedload

from src.database.engine_db import Session  # Импортируем Session
from src.database.models.match import Match
from src.database.models.player import Player

# Константы для счета (например, количество выигранных геймов для победы в сете)
GAMES_TO_WIN_SET = 6
MIN_GAMES_DIFF = 2


def create_match(parsed_data):
    """Создает новый матч."""
    player1_name = parsed_data.get('player1_name', [''])[0]
    player2_name = parsed_data.get('player2_name', [''])[0]

    with Session() as session:
        # Создаем или находим игроков за один запрос
        player1 = session.query(Player).filter_by(name=player1_name).first() or Player(name=player1_name)
        player2 = session.query(Player).filter_by(name=player2_name).first() or Player(name=player2_name)

        if not player1.id:
            session.add(player1)
        if not player2.id:
            session.add(player2)
        session.commit()
        # Создаем новый матч
        match_uuid = str(uuid.uuid4())
        new_match = Match(
            uuid=match_uuid,
            player1_id=player1.id,
            player2_id=player2.id,
            winner_id=None,
            score=json.dumps({
                "sets": [],
                "player1": {"games": 0, "sets": 0},
                "player2": {"games": 0, "sets": 0}
            })
        )
        session.add(new_match)
        session.commit()

    return match_uuid


def get_match_score(match_uuid):
    """Получает информацию о счете матча."""
    with Session() as session:
        match = session.query(Match).options(
            joinedload(Match.player1),
            joinedload(Match.player2)
        ).filter_by(uuid=match_uuid).first()

        if not match:
            return None
        return match, session


def update_match_score(match, winner, session):
    """Обновляет счет матча."""
    if match.score is None:
        match.score = json.dumps({
            'sets': [],
            'player1': {'games': 0, 'sets': 0},
            'player2': {'games': 0, 'sets': 0}
        })
    score_data = json.loads(match.score)

    # Проверяем, что счет содержит все необходимые ключи
    if 'sets' not in score_data:
        score_data['sets'] = []
    if 'player1' not in score_data:
        score_data['player1'] = {'games': 0, 'sets': 0}
    if 'player2' not in score_data:
        score_data['player2'] = {'games': 0, 'sets': 0}

    current_set_index = len(score_data['sets']) - 1
    if current_set_index < 0 or is_set_finished(score_data['sets'][current_set_index]):
        score_data['sets'].append([0, 0])
        current_set_index += 1

    if winner == 'player1':
        score_data['sets'][current_set_index][0] += 1
    elif winner == 'player2':
        score_data['sets'][current_set_index][1] += 1

    # Проверяем, закончился ли сет
    if is_set_finished(score_data['sets'][current_set_index]):
        if score_data['sets'][current_set_index][0] > score_data['sets'][current_set_index][1]:
            score_data['player1']['sets'] += 1
        else:
            score_data['player2']['sets'] += 1

    match.score = json.dumps(score_data)

    session.add(match)
    session.commit()


def is_set_finished(set_score):
    """Проверяет, закончился ли сет."""
    player1_games, player2_games = set_score
    return ((player1_games >= GAMES_TO_WIN_SET or player2_games >= GAMES_TO_WIN_SET) and
            abs(player1_games - player2_games) >= MIN_GAMES_DIFF)


def get_winner_id(score_data, match):
    """Возвращает ID победителя или None, если ничья."""
    player1_sets = score_data.get('player1', {}).get('sets', 0)
    player2_sets = score_data.get('player2', {}).get('sets', 0)
    if player1_sets > player2_sets:
        return match.player1_id  # player1_id
    elif player2_sets > player1_sets:
        return match.player2_id  # player2_id
    else:
        return None  # Ничья (маловероятно в теннисе)
