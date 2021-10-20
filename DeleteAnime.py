import DataBase
import ShowAll


class DeleteAnime:
    def __init__(self):
        self.__database = DataBase.DataBase()

    def delete_one_anime(self, update, context):
        anime_id = update.callback_query.data.split('/')[1]
        chat_id = update.effective_chat.id
        message_id = str(update.callback_query.message.message_id)

        self.__database.delete_anime_from_links(chat_id, anime_id)

        settings = self.__database.select_chat_settings(chat_id)
        __message_pagination_ids = settings[0][2]
        __pagination_pages = settings[0][3]
        message_ids = __message_pagination_ids.split(';')
        message_ids.remove(message_id)
        self.__database.settings_update_mess_ids(chat_id, ';'.join(message_ids), __pagination_pages)

        context.bot.deleteMessage(
            update.effective_chat.id,
            message_id,
        )

        __show_all = ShowAll.ShowAll(chat_id)
        __show_all.show_all(update, context)
