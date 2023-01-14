import logging
import CheckRss
import DeleteAnime
import Start
import ShowAll
import SecretInfo
import Settings
import DataBase
import Add
import BotUpdates
import Downloader
import Viewer

from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALL, ADD_LINK, SETTINGS_CHECK_PAGINATION = range(3)


class WatchingFilms:
    def __init__(self):
        self.__start = Start.Start()
        self.__settings = Settings.Settings()
        self.__delete_anime = DeleteAnime.DeleteAnime()
        self.__add = Add.Add()
        self.__show_all = None
        self.database = DataBase.DataBase()
        self.database.check_or_create_db()
        self.dispatcher = ''

    def create_init_params(self, update):
        self.__show_all = ShowAll.ShowAll(update.effective_chat.id)

    def start(self, update, context):
        self.__start.start(update, context)
        return SETTINGS_CHECK_PAGINATION

    def second_start(self, update, context):
        self.__start.second_start(update, context)
        return SETTINGS_CHECK_PAGINATION

    def setting_check_pagination(self, update, context):
        self.__settings.settings_ready(update, context)
        return ALL

    def add(self, update, context):
        self.__add.add(update, context)
        return ADD_LINK

    def enter_link(self, update, context):
        self.__add.add_link(update, context)
        return ALL

    def cancel_add(self, update, context):
        self.__add.cancel_add(update, context)
        return ALL

    def show_all(self, update, context):
        if self.__show_all is None:
            self.create_init_params(update)
        self.__show_all.show_all(update, context)
        return ALL

    def show_pagination_page(self, update, context):
        if self.__show_all is None:
            self.create_init_params(update)
        self.__show_all.show_pagination_page(update, context)

    def delete_anime(self, update, context):
        self.__delete_anime.delete_one_anime(update, context)
        return ALL

    def download_anime(self, update, context):
        """
        @deprecated
        :param update:
        :param context:
        :return:
        """
        link = update.callback_query.data.split('/')[1]
        chat_id = update.effective_chat.id
        Downloader.get(link, chat_id)

    def get_serieses(self, update, context):
        link_id = update.callback_query.data.split('/')[1]
        chat_id = update.effective_chat.id
        Viewer.get_all(link_id, chat_id)

    def main(self):
        updater = Updater(SecretInfo.TELEGRAM_HTTP_API_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        self.dispatcher = dispatcher

        # self.update_restart()

        control_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start),
                MessageHandler(Filters.regex('Просмотреть список'), self.show_all),
                MessageHandler(Filters.regex('Добавить аниме'), self.add),
                MessageHandler(Filters.regex('Отмена'), self.cancel_add),
                CallbackQueryHandler(self.delete_anime, pass_user_data=True, pattern="anime/"),
                CallbackQueryHandler(self.show_pagination_page, pass_user_data=True, pattern="page/"),
                CallbackQueryHandler(self.get_serieses, pass_user_data=True, pattern="view/"),
            ],
            states={
                SETTINGS_CHECK_PAGINATION: [
                    MessageHandler(Filters.regex(r"^(?:[1-9]\d*(?:\.\d+)?|0\.0*[1-9]\d*)$"),
                                   self.setting_check_pagination)
                ],
                ALL: [
                    # CommandHandler('start', self.start),
                    CommandHandler('start', self.second_start),
                    MessageHandler(Filters.regex('Просмотреть список'), self.show_all),
                    MessageHandler(Filters.regex('Добавить аниме'), self.add),
                    CallbackQueryHandler(self.delete_anime, pass_user_data=True, pattern="anime/"),
                    CallbackQueryHandler(self.show_pagination_page, pass_user_data=True, pattern="page/"),
                ],
                ADD_LINK: [
                    MessageHandler(Filters.regex('Отмена'), self.cancel_add),
                    MessageHandler(Filters.text, self.enter_link),
                ]
            },
            fallbacks=[],
        )

        dispatcher.add_handler(control_handler)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    watchingFilms = WatchingFilms()
    update_bot = BotUpdates.BotUpdates()
    check_rss = CheckRss.CheckRss()
    check_rss.start_thread()
    watchingFilms.main()
