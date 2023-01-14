import math
import DataBase
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class ShowAll:
    def __init__(self, chat_id):
        self.__database = DataBase.DataBase()
        settings = self.__database.select_chat_settings(chat_id)
        self.__anime_in_one_pagination = settings[0][1]
        self.__message_pagination_ids = settings[0][2]
        self.__pagination_pages = settings[0][3]

    def show_all(self, update, context, offset=0):
        settings = self.__database.select_chat_settings(update.effective_chat.id)
        self.__anime_in_one_pagination = settings[0][1]
        self.__message_pagination_ids = settings[0][2]
        self.__pagination_pages = settings[0][3]
        __message_pagination_ids = []
        paged_info = self.__database.get_anime_list(update.effective_chat.id,
                                                  int(offset) * int(self.__anime_in_one_pagination),
                                                  self.__anime_in_one_pagination)
        all_info = self.__database.get_all_anime_list(update.effective_chat.id)[0][0]
        pages = math.ceil(all_info / int(self.__anime_in_one_pagination))

        buttons_page = []
        for index in range(pages):
            buttons_page.append(InlineKeyboardButton(f"{index+1}", callback_data=f"page/{index}"),)
        __reply_keyboard = [
            buttons_page,
        ]

        self.clear_mess(update, context)
        for item in paged_info:
            keyboard = [[
                InlineKeyboardButton('Удалить', callback_data=f"anime/{item[0]}"),
                InlineKeyboardButton('Скачать', callback_data=f"view/{item[0]}"),
            ], ]
            message = context.bot.send_message(
                update.effective_chat.id,
                text=F"{item[2]}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            __message_pagination_ids.append(str(message.message_id))
        self.__message_pagination_ids = ';'.join(__message_pagination_ids)

        if pages > 1:
            message = context.bot.send_message(
                update.effective_chat.id,
                text='Страницы',
                reply_markup=InlineKeyboardMarkup(__reply_keyboard)
            )
            self.__pagination_pages = message.message_id

        self.__database.settings_update_mess_ids(update.effective_chat.id, self.__message_pagination_ids,
                                                 self.__pagination_pages)

    def show_pagination_page(self, update, context):
        page = update.callback_query.data.split('/')
        self.show_all(update, context, int(page[1]))

    def clear_mess(self, update, context):
        if self.__message_pagination_ids is not None:
            message_ids = self.__message_pagination_ids.split(';')
            if len(message_ids) > 0:
                for index in range(len(message_ids)):
                    try:
                        context.bot.deleteMessage(
                            update.effective_chat.id,
                            message_ids.pop(0),
                        )
                    except Exception :
                        pass
                # print(f" self.__message_pagination_id = { self.__pagination_pages}")
                if self.__pagination_pages != 0:
                    try:
                        context.bot.deleteMessage(
                            update.effective_chat.id,
                            self.__pagination_pages,
                        )
                    except Exception :
                        pass
