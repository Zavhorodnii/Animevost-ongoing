from telegram import ReplyKeyboardMarkup

from DataBase import DataBase


class Add:
    def __init__(self):
        self.__cancel_keyboard = [
            ['Отмена'],
        ]
        self.__control_keyboard = [
            ['Просмотреть список', 'Добавить аниме'],
        ]

    def add(self, update, context):
        context.bot.send_message(
            update.effective_chat.id,
            text=f"Введите ссылку",
            reply_markup=ReplyKeyboardMarkup(self.__cancel_keyboard, resize_keyboard=True, one_time_keyboard=False)
        )

    def add_link(self, update, context):
        DataBase().add_anime_to_db(update.effective_chat.id, update.message.text)

        context.bot.send_message(
            update.effective_chat.id,
            text=f"Тайтл добавлен",
            reply_markup=ReplyKeyboardMarkup(self.__control_keyboard, resize_keyboard=True, one_time_keyboard=False)
        )

    def cancel_add(self, update, context):
        __reply_keyboard = [
            ['Просмотреть список', 'Добавить аниме'],
        ]

        context.bot.send_message(
            update.effective_chat.id,
            text=f"Вы отменили добавление тайтла",
            reply_markup=ReplyKeyboardMarkup(__reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        )