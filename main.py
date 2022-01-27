import logging
import csv
import yaml
from datetime import date
from telethon import TelegramClient, sync
from telethon.hints import Entity

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

# Создадим справочник контактов что бы каждый раз не посылать запрос на сервер
dialogs = client.get_dialogs()
contacts = {}
for chat in dialogs:
    if chat.is_user is True and chat.name != '' and chat.title != '':
        contacts.update({chat.id:chat.name})
        logging.debug(f'Получен чат № {chat.id} с {contacts[chat.id]}')

# Метод что бы получить все текстовые сообщения чата
def chat2file(username):
    try:
        with open(f'chat_with_{contacts[username]}.csv', mode="w", encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\r")
            file_writer.writerow(['id', 'date', 'sender', 'text'])

            messages = client.get_messages(username, None, reverse=True)
            counter = len(messages)
            logging.info(f'Чат содержит {counter} сообщений:')
            for sms in messages:
                if sms.message != '' and sms.message is not None:
                    file_writer.writerow([sms.id, sms.date.strftime("%d-%m-%Y %H:%M"), contacts[sms.sender_id], sms.text])
                    logging.debug(counter)
                    counter -= 1
                    logging.debug(f'Сообщение {sms.id} записно в файл chat_with_{username}.txt')
            logging.info(f'{counter} из {len(messages)} сообщений не текст')
    except TypeError as e:
        print(e)
        pass



# В секретах храним список чатов для загрузки
CHAT_IDs = secrets['CHAT_IDs']

# Скачаем все эти чаты
for chat in CHAT_IDs:
    chat2file(chat)

print('Готово!')