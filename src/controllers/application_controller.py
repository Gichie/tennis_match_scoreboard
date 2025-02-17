from werkzeug.wrappers import Response
import src.utils as utils
from src.controllers.match_controller import create_match, get_match_score, update_match_score


def handle_index(request):
    """Обрабатывает запрос на главную страницу."""
    return Response(utils.render_template("index.html"), content_type="text/html")


def handle_new_match(request):
    """Обрабатывает запрос на создание нового матча."""
    if request.method == "POST":
        form_data = request.form
        match_uuid = create_match(form_data)
        return Response(f"Match created: {match_uuid}", status=302,
                        headers={"Location": f"/match_score?uuid={match_uuid}"})


def handle_match_score(request):
    """Обрабатывает запрос на отображение счета матча."""
    match_uuid = request.args.get("uuid")
    if not match_uuid:
        return Response("Missing match UUID", status=400)

    match = get_match_score(match_uuid)
    if not match:
        return Response("Match not found", status=404)

    score_table_html = utils.render_score_table(match)
    game_buttons_html = utils.render_game_buttons(match, match_uuid)
    final_score_html = utils.render_final_score(match) if match.winner_id else ''

    template = utils.render_template("match_score.html", {
        "match_uuid": match_uuid,
        "score_table": score_table_html,
        "game_buttons": game_buttons_html,
        "final_score": final_score_html,
    })
    return Response(template, content_type="text/html")
