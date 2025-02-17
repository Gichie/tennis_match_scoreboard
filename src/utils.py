from jinja2 import Environment, FileSystemLoader
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Абсолютный путь к директории app.py


env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')),  # Загрузка шаблонов из директории templates
    autoescape=True  # Включаем автозамещение для предотвращения XSS
)

def url_for_static(filename):
    """Формирует URL для статических файлов."""
    return f"/static/{filename}"

def render_template(template_name, context={}):
    """Рендерит HTML-шаблон с использованием Jinja2."""
    context["static_url"] = url_for_static  # Добавляем url_for_static в контекст
    template = env.get_template(template_name)
    return template.render(context)


def render_score_table(match):
    """Генерирует HTML-код таблицы счета для матча."""
    return render_template("partials/score_table.html", {"match": match})


def render_game_buttons(match, match_uuid):
    """Генерирует HTML-кнопки управления игрой."""
    return render_template("partials/game_buttons.html", {"match": match, "match_uuid": match_uuid})


def render_final_score(match):
    """Генерирует финальный счет матча, если он завершен."""
    return render_template("partials/final_score.html", {"match": match})