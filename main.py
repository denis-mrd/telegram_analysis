import logging
import yaml
import psycopg2
from datetime import date
from telethon import TelegramClient, sync

# Начинаем вести журнал работы программы
logging.basicConfig(filename="my.log", level=logging.DEBUG)

# Откроем файлик с секретами
with open("secrets.yaml", "r") as f:
    try:
        secrets = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)

# Вставляем API_ID и API_HASH из файла
API_ID = secrets['API_ID']
API_HASH = secrets['API_HASH']

# Начинаем сессию в телеге. Надо ввести номер телефона, одноразовый код и пароль от телеги
client = TelegramClient(str(date.today()), API_ID, API_HASH)
client.start()

# Подключаемся к базе
conn = psycopg2.connect(dbname=secrets['DB_NAME'], user=secrets['DB_USER'], password=secrets['DB_PWD'], host=secrets['DB_HOST'])

# Создадим справочник контактов
dialogs = client.get_dialogs()
for chat in dialogs:
    try:
        with conn.cursor() as cursor:
            if chat.is_user is True and chat.name != '' and chat.title != '':
                query = f"INSERT INTO dialogs (sender_id, name, title) VALUES ({chat.id}, '{chat.name}', '{chat.title}');"
                cursor.execute(query)
                conn.commit()
                logging.debug(f'Получен чат № {chat.id} с {chat.name}')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

# Метод что бы получить все текстовые сообщения чата
def save_chat(chat_id):
    try:
        with conn.cursor() as cursor:
            messages = client.get_messages(chat_id, None, reverse=True)
            counter = len(messages)
            logging.info(f'Чат содержит {counter} сообщений:')
            for sms in messages:
                if sms.message != '' and sms.message is not None:  
                    query = f"INSERT INTO messages (chat_id, message_id, date, sender_id, text) VALUES ({sms.chat_id}, {sms.id}, '{sms.date}', {sms.sender_id}, '{sms.text}');"
                    cursor.execute(query)
                    conn.commit()
                    logging.debug(counter)
                    counter -= 1
                    logging.debug(f'Сообщение {sms.id} записно')
            logging.info(f'{counter} из {len(messages)} сообщений не текст')
            cursor.close()
            conn.close()
    except TypeError as error:
        print(error)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

# В секретах храним список чатов для загрузки
CHAT_IDs = secrets['CHAT_IDs']

# Скачаем все эти чаты
for chat in CHAT_IDs:
    save_chat(chat)

print('Готово!')