from jinja2 import Environment, FileSystemLoader
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Абсолютный путь к директории app.py


env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')),  # Загрузка шаблонов из директории templates
    autoescape=True  # Включаем автозамещение для предотвращения XSS
)


def render_template(template_name, context={}):
    """Рендерит HTML-шаблон с использованием Jinja2."""
    template = env.get_template(template_name)  # Получаем шаблон
    return template.render(context)  # Рендерим шаблон с подстановкой данных
