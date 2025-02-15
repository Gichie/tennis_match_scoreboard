import logging
from http.server import HTTPServer

from src.app import RequestHandler

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info('Запуск сервера по адресу http://localhost:8000/')

        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nСервер остановлен.')
    except Exception as e:
        print(f'Ошибка: {e}')
    finally:
        httpd.server_close()
