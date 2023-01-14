import telegram
import xmltodict as xmltodict
from telegram.ext import Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import urllib.parse

import DataBase
from threading import Thread
from time import sleep

import requests

import SecretInfo
import Downloader


class CheckRss:
    def __init__(self,):
        updater = Updater(SecretInfo.TELEGRAM_HTTP_API_TOKEN, use_context=True)
        self.dispatcher = updater.dispatcher
        self.context = telegram.ext.callbackcontext.CallbackContext(self.dispatcher)
        self.rss_url = 'https://animevost.org/rss.xml'
        self.anime_rss_last_anime = ''
        self.__database = DataBase.DataBase()
        # self.__database.clear_last_anime()

    def start_thread(self):
        thread = Thread(target=self.chek_rss, args=())
        thread.start()

    def update_last_anime(self, dict_data, index):
        self.anime_rss_last_anime = ''
        # self.anime_rss_last_anime.append(dict_data['rss']['channel']['item'][index]['title'])
        parsed = urllib.parse.urlparse(dict_data['rss']['channel']['item'][index]['link'])
        replaced = parsed._replace(netloc="animevost.org")
        self.anime_rss_last_anime = urllib.parse.urlunparse(replaced)

    def chek_rss(self):
        while True:
            try:
                response = requests.get(
                    url=self.rss_url,
                )
                dict_data = xmltodict.parse(response.content)
            except Exception as exe:
                sleep(10)
                continue

            if len(self.anime_rss_last_anime) == 0:
                last_rss = self.__database.get_last_anime()[0][0]
                if len(last_rss) > 0:
                    self.anime_rss_last_anime = last_rss
                else:
                    self.update_last_anime(dict_data, len(dict_data['rss']['channel']['item']) - 1)
                    self.__database.update_last_anime(self.anime_rss_last_anime)
                continue

            # print(f"self.anime_rss_last_anime = {self.anime_rss_last_anime}")

            for elem in dict_data['rss']['channel']['item']:
                parsed = urllib.parse.urlparse(elem['link'])
                replaced = parsed._replace(netloc="animevost.org")
                elem['link'] = urllib.parse.urlunparse(replaced)

                in_anime_dict = False

                if elem['link'] == self.anime_rss_last_anime:
                    # print(f"in_anime_dict link = { elem['link']}, title = {elem['title']}")
                    in_anime_dict = True

                if in_anime_dict:
                    if dict_data['rss']['channel']['item'][0]['link'] != self.anime_rss_last_anime:
                        self.update_last_anime(dict_data, 0)
                        self.__database.update_last_anime(self.anime_rss_last_anime)
                    break

                all_chats = self.__database.get_all_chat_with_anime(elem['link'])
                # print(f"send to chat = {all_chats}")
                if len(all_chats) > 0:

                    dlink = Downloader.parse_last(elem['link'])

                    keyboard = [[
                        InlineKeyboardButton('Скачать 480p - ' + dlink['title'], url=dlink['link']),
                        InlineKeyboardButton('Скачать 720p - ' + dlink['title'], url=dlink['link720']),
                    ], ]

                    for chat_id in all_chats:
                        try:
                            message = self.context.bot.send_message(
                                chat_id[0],
                                text=F"Новый эпизод\n\n{elem['title']}\n\n{elem['link']}",
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            )
                        except Exception as exe:
                            continue

                if dict_data['rss']['channel']['item'][len(dict_data['rss']['channel']['item']) - 1]['link'] == elem['link']:
                    if dict_data['rss']['channel']['item'][0]['link'] != self.anime_rss_last_anime:
                        self.update_last_anime(dict_data, 0)
                        self.__database.update_last_anime(self.anime_rss_last_anime)

            sleep(300)
