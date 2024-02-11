import DataBase
import Downloader
import math
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_all(update, context):
    params = update.callback_query.data.split('/')
    link_id = params[1]
    offset = 0
    chat_id = update.effective_chat.id

    if len(params) > 2:
        offset = int(params[2])

    db = DataBase.DataBase()

    links = db.get_anime_link_by_id(link_id)
    if len(links) == 0:
        return

    serieses = Downloader.parse_all(links[0][0])

    __clear_messages(chat_id, context)

    keyboard = []

    items = serieses['items']

    size = len(items)
    index = offset * 27
    count = 0

    while index < size and count < 27:
        line = []
        i = 0
        while i < 3 and count < size:
            line.append(InlineKeyboardButton(items[index]['title'], url=items[index]['link720']),)
            index = index + 1
            count = count + 1
            i = i + 1
        keyboard.append(line)

    message = context.bot.send_message(
        chat_id,
        text=F"{links[0][0]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    last_messages = message.message_id
    last_pagination = 0

    pages = math.ceil(size / 27)

    keyboard = []

    if pages > 1:
        index = 0
        while index < pages:
            line = []
            i = 0
            while i < 8 and index < pages:
                line.append(InlineKeyboardButton(f"{index+1}", callback_data=f"view/{link_id}/{index}"),)
                index = index + 1
                i = i + 1
            keyboard.append(line)

        message = context.bot.send_message(
            chat_id,
            text='Страницы',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        last_pagination = message.message_id

    db.settings_update_mess_ids(chat_id, last_messages, last_pagination)


def __clear_messages(chat_id, context):
    settings = DataBase.DataBase().select_chat_settings(chat_id)
    if len(settings) == 0:
        return
    message_pagination_ids = settings[0][2]
    pagination_pages = settings[0][3]

    if message_pagination_ids is not None:
        message_ids = message_pagination_ids.split(';')
        if len(message_ids) > 0:
            for index in range(len(message_ids)):
                try:
                    context.bot.deleteMessage(
                        chat_id,
                        message_ids.pop(0),
                    )
                except Exception:
                    pass
            if pagination_pages != 0:
                try:
                    context.bot.deleteMessage(
                        chat_id,
                        pagination_pages,
                    )
                except Exception:
                    pass