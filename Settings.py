from telegram import ReplyKeyboardMarkup

from DataBase import DataBase


class Settings:

    def __init__(self):
        pass

    def settings_ready(self, update, context):
        pagination = update.message.text
        DataBase().add_chat(update.effective_chat.id, pagination)

        __reply_keyboard = [
            ['Просмотреть список', 'Добавить аниме'],
        ]

        context.bot.send_message(
            update.effective_chat.id,
            text=f"Отлично! \n\n"
                 "Настройки завершены",
            reply_markup=ReplyKeyboardMarkup(__reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        )

        return int(pagination)
