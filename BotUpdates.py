import BotSettings
import DataBase
import SecretInfo
import telegram
from telegram.ext import Updater


class BotUpdates:
    version = '1.2.0'
    description = 'Обновление до версии 1.2.0:\n- В уведомлении о новой серии доступна ссылка на скачивание файла в качестве 720р'

    def __init__(self):
        updater = Updater(SecretInfo.TELEGRAM_HTTP_API_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        context = telegram.ext.callbackcontext.CallbackContext(dispatcher)
        settings = BotSettings.BotSetting()
        version = settings.get("version")

        db = DataBase.DataBase()

        if version != BotUpdates.version and BotUpdates.description != '':
            users = db.get_active_users()
            for user in users:
                try:
                    message = context.bot.send_message(
                        user[0],
                        text=BotUpdates.description,
                    )
                except Exception as exe:
                    print(exe)

            settings.update("version", BotUpdates.version)
