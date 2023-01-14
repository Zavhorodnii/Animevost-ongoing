import DataBase
import Downloader
import SecretInfo
import telegram
from telegram.ext import Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_all(link_id, chat_id):
    links = DataBase.DataBase().get_anime_link_by_id(link_id)
    if len(links) == 0:
        return

    serieses = Downloader.parse_all(links[0][0])

    updater = Updater(SecretInfo.TELEGRAM_HTTP_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    context = telegram.ext.callbackcontext.CallbackContext(dispatcher)

    __clear_messages(chat_id, context)

    keyboard = []

    items = serieses['items']

    for index in range(len(items)):
        line = []
        for i in range(3):
            line.append(InlineKeyboardButton(items[index]['title'], url=items[index]['link']),)
            index = index + 1
        keyboard.append(line)

    message = context.bot.send_message(
        chat_id,
        text=F"{links[0][0]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


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