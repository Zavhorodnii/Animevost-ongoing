import DataBase
import SecretInfo
import re
import requests
from threading import Thread
import telegram
from telegram.ext import Updater


def parse_last(link):
    result = parse_all(link)
    last = result['items'][-1]
    return last


def parse_all(link):
    db = DataBase.DataBase()

    response = requests.get(
        url=link,
    )
    # print(response.text)

    # заголовок
    match = re.search(r'property=\"og:title\" content=\".+?/', response.text)
    anime_title = match[0].split('\"')[-1].split('/')[0]

    # список серий
    items = []
    match = re.search(r'var data = \{\".+?\}', response.text)[0].split('{')[1].replace('}', '')

    for item in match.split(','):
        if item == '' or item == ' ':
            continue
        item = item.split(':')

        name = item[0].replace('\"', '')
        link = item[1].replace('\"', '')
        full_name = anime_title + name

        items.append({
            'link': link,
            'title': name,
            'full_title': full_name,
        })

        name = db.get_series_name_by_link(link)
        if len(name) == 0:
            db.insert_series(link, full_name + '.mp4')

    return {
        'items': items,
        'title': anime_title
    }


def get(link, user):
    if link not in TaskManager.tasks:
        TaskManager.tasks[link] = DownloadTask(link)
    TaskManager.tasks[link].add_user(user)


class TaskManager:
    tasks = {}


class DownloadTask:

    def __init__(self, link):
        # ссылка на серию
        self.__link = link
        # id скаченного файла или id сообщения для пересылки
        self.__file = None
        # список людей, котоыре подписались на скачивание серии
        self.__users = []
        # номер серии для подписи файла
        self.__number = 0
        # заголовок для серии
        self.__title = self.get_title()
        thread = Thread(target=self.run_task, args=())
        thread.start()

    def run_task(self):

        if not self.get_file_id():
            with requests.get('https://static.trn.su/' + self.__link + '.mp4', stream=True) as r:
                r.raise_for_status()
                with open(self.__title, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        self.notify_users()

    def get_title(self):
        db = DataBase.DataBase()
        name = db.get_series_name_by_link(self.__link)
        if len(name) > 0:
            return name[0][0]

        return ''

    def get_file_id(self):
        db = DataBase.DataBase()
        items = db.get_anime_file_id_by_link(self.__link)
        if len(items) > 0:
            self.__file = items[0][0]
            return True
        return False

    def add_user(self, user):
        self.__users.append(user)
        if self.__file is not None:
            self.notify_users()

    def notify_users(self):
        updater = Updater(SecretInfo.TELEGRAM_HTTP_API_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        context = telegram.ext.callbackcontext.CallbackContext(dispatcher)

        for user in self.__users:

            if self.__file is None:
                message = context.bot.send_document(chat_id=user, document=self.__title)
                self.__file = message.document.file_id
                db = DataBase.DataBase()
                db.insert_downloaded_anime(self.__link, self.__file)
            else:
                message = context.bot.send_document(chat_id=user, document=self.__file)

            self.__users.remove(user)
