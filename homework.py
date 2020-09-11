import logging
import os
import time

from dotenv import load_dotenv
import requests
import telegram

load_dotenv()

logging.basicConfig(level=logging.ERROR, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):

    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('Не удалось получить данные дз, homework_name is None')
        return f'Не удалось получить данные дз, homework_name is None'
    homework_status = homework.get('status')
    if homework_status is None:
        logging.error('Не удалось получить данные дз, homework_status is None')
        return f'Не удалось получить данные дз, homework_status is None'

    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему ' \
                  'уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(url, headers=headers,
                                         params={
                                             'from_date': current_timestamp})
        return homework_statuses.json()
    except Exception as e:
        print(f'Не удалось проверить статус дз: {e}')
        logging.error("Exception occurred", exc_info=True)


def send_message(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        return bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f'Не удалось отправить сообщение: {e}')
        logging.error("Exception occurred", exc_info=True)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
