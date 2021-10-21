
class Start:

    def start(self, update, context):
        context.bot.send_message(
            update.effective_chat.id,
            text="Здравствуй!\n\n"
                 "Так как это наше первое знакомство, давайте проведем некоторые настройки",
        )
        context.bot.send_message(
            update.effective_chat.id,
            text="Начнем с пагинации\n\n"
                 "Введите число, которое будет является количеством аниме на одной странице",
        )