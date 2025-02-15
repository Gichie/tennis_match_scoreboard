import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

from src.controllers.match_controller import (create_match, get_match_score, update_match_score, get_winner_id)

from src.database.engine_db import engine

from src.database.models.player import Player
from sqlalchemy.orm import sessionmaker
from src import utils

Session = sessionmaker(bind=engine)

# Константы для счета (например, количество выигранных геймов для победы в сете)
GAMES_TO_WIN_SET = 6
MIN_GAMES_DIFF = 2


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path in ('/', '/index.html', '/new_match.html', '/finished_matches.html'):
            try:
                template_name = path.split('/')[-1]  # Получаем имя шаблона из пути
                if template_name == '':
                    template_name = 'index.html'
                template = utils.render_template(template_name)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(template.encode('utf-8'))

            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()

        elif path.startswith('/match_score'):  # Обработка страницы счета матча
            parsed_query = urlparse(self.path).query
            match_uuid = parse_qs(parsed_query).get('uuid', [None])[0]

            print(f"Обработка GET /match_score, uuid = {match_uuid}")  # Добавляем логирование

            if not match_uuid:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing match UUID')
                return
            match, session = get_match_score(match_uuid)
            if not match:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Match not found')
                return

            score_table_html = self.render_score_table(match)
            game_buttons_html = self.render_game_buttons(match, match_uuid)
            final_score_html = ''
            if match.winner_id:
                final_score_html = self.render_final_score(match, session)
                game_buttons_html = ''
            template_name = 'match_score.html'
            template = utils.render_template(template_name, {
                'match_uuid': match_uuid,
                'score_table': score_table_html,
                'game_buttons': game_buttons_html,
                'final_score': final_score_html,
            })
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(template.encode('utf-8'))

        elif path.endswith('.css'):
            try:
                file_path = os.path.join('src', 'static', 'css', path.split('/')[-1])
                with open(file_path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/css')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/new-match':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = parse_qs(post_data)
            match_uuid = create_match(parsed_data)
            # Перенаправляем на страницу счета матча
            self.send_response(302)
            self.send_header('Location', f'/match_score?uuid={match_uuid}')
            self.end_headers()

        elif path.startswith('/match_score'):  # Обработка POST-запросов для обновления счета
            parsed_query = parse_qs(urlparse(self.path).query)
            match_uuid = parsed_query.get('uuid', [None])[0]
            print(f'Логи match_uuid: {match_uuid}')

            if not match_uuid:
                self.send_response(400)  # Bad Request
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing match UUID')
                return
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = parse_qs(post_data)
            winner = parsed_data.get('winner', [None])[0]  # Получаем победителя очка
            print(f'Логи winner: {winner}')

            match, session = get_match_score(match_uuid)
            if not match:
                self.send_response(404)  # Not Found
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Match not found')
                return
            # Обновляем счет
            if winner == 'player1':
                update_match_score(match, 1, session)
            elif winner == 'player2':
                update_match_score(match, 2, session)
            # Перенаправляем на страницу счета матча
            self.send_response(302)
            self.send_header('Location', f'/match_score?uuid={match_uuid}')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    @staticmethod
    def render_score_table(match):
        """Формирует HTML-таблицу со счетом."""
        player1_name = match.player1.name
        player2_name = match.player2.name
        if match.score:
            score_data = json.loads(match.score)
            sets = score_data.get('sets', [])
            player1_sets = score_data.get('player1', {}).get('sets', 0)
            player2_sets = score_data.get('player2', {}).get('sets', 0)
            score_table_html = f"""
                <div class="score-table-container"> 
                    <table>
                        <thead>
                            <tr>
                                <th>Игрок</th>
                                <th>Сеты</th>
                                {''.join(f'<th>Сет {i + 1}</th>' for i in range(len(sets)))}
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{player1_name}</td>
                                <td>{player1_sets}</td>
                                {''.join(f'<td>{s[0]}</td>' for s in sets)}
                            </tr>
                            <tr>
                                <td>{player2_name}</td>
                                <td>{player2_sets}</td>
                                {''.join(f'<td>{s[1]}</td>' for s in sets)}
                            </tr>
                        </tbody>
                    </table>
                </div>
            """
        else:
            score_table_html = f"""
                <div class="score-table-container">
                    <p>Матч еще не начался.</p>
                </div>
            """
        return score_table_html

    @staticmethod
    def render_game_buttons(match, match_uuid):
        """Формирует HTML для кнопок добавления очков."""
        if not match.winner_id:
            game_buttons_html = f"""
                <div class="score-buttons">
                    <button onclick="location.href='/match_score?uuid={match_uuid}&winner=player1'">Игрок 1 выиграл очко</button>
                    <button onclick="location.href='/match_score?uuid={match_uuid}&winner=player2'">Игрок 2 выиграл очко</button>
                </div>
            """
        else:
            game_buttons_html = ''
        if not match.score:
            game_buttons_html = f"""<div class = "start_message"><p>Матч еще не начался.</p> </div> {game_buttons_html}"""

        return game_buttons_html

    def render_final_score(self, match, session):
        """Формирует HTML для отображения финального счета."""
        score_data = json.loads(match.score)
        score_table_html = self.render_score_table(match)
        winner_id = get_winner_id(score_data, match)  # self.get_winner_id(score_data)
        winner_name = session.query(Player).get(winner_id).name if winner_id else "Ничья"
        final_score_html = f"""
                    <h2>Финальный счет</h2>
                    <div id="final_score_table">
                        {score_table_html}
                    </div>
                    <p>Победитель: <span id="winner_name">{winner_name}</span></p>
                """
        return final_score_html
