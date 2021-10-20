
class Start:

    def start(self, update, context):
        context.bot.send_message(
            update.effective_chat.id,
            text="Здравствуй!\n\n"
                 "Так как это наше первое знакомство, давай проведем некоторые настройки",
        )
        context.bot.send_message(
            update.effective_chat.id,
            text="Начнем с пагинации\n\n"
                 "Введи число, которое будет является количеством фильмов на одной странице",
        )