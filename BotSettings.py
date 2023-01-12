import DataBase


class BotSetting:

    __settings = None

    def __init__(self):
        self.load_settings()

    def load_settings(self):

        if BotSetting.__settings is not None:
            return

        db = DataBase.DataBase()
        settings = db.load_bot_settings()
        BotSetting.__settings = {}

        for line in settings:
            BotSetting.__settings[line[0]] = line[1]

    def get(self, key):
        if key in BotSetting.__settings:
            return BotSetting.__settings[key]

        return ''

    def update(self, key, value):

        db = DataBase.DataBase()
        if key in BotSetting.__settings:
            db.update_bot_setting(key, value)
        else:
            db.add_bot_setting(key, value)

        BotSetting.__settings[key] = value