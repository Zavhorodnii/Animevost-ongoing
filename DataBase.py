# import pymysql as pymysql
import psycopg2
import os

class DataBase:
    def __init__(self):
        # self.__my_db_connector = pymysql.connect(
        #      host='localhost',
        #      user='root',
        #      password='root',
        #      database='watching_films_bot',
        #      charset='utf8mb4',
        # )
        # self.__my_db_connector = None
        self.__check_or_create_database = "CREATE DATABASE IF NOT EXISTS animevost_ongoing;"

        self.__create_db_table_settings = "CREATE TABLE IF NOT EXISTS settings(" \
                                      "chat_id VARCHAR(100), " \
                                      "films_in_one_pagination INT DEFAULT '5', " \
                                      "last_messages TEXT, " \
                                      "last_pagination VARCHAR(10) DEFAULT '0')"

        self.__create_db_table_links = "CREATE TABLE IF NOT EXISTS links(" \
                                      "id SERIAL, " \
                                      "chat_id VARCHAR(100), " \
                                      "link TEXT )"

        self.__create_db_table_last_anime = "CREATE TABLE IF NOT EXISTS last_anime( " \
                                            "id SERIAL, " \
                                            "last_anime_in_rss TEXT)"

        self.__create_db_table_anime_download = "CREATE TABLE IF NOT EXISTS anime_download( " \
                                                "link TEXT NOT NULL," \
                                                "flie_id BIGINT NOT NULL)"

        self.__create_db_table_series = "CREATE TABLE IF NOT EXISTS series( " \
                                        "link TEXT NOT NULL," \
                                        "name TEXT NOT NULL)"

        self.__create_db_table_bot_settings = "CREATE TABLE IF NOT EXISTS bot_settings( " \
                                              "key VARCHAR(100) NOT NULL," \
                                              "value VARCHAR(100) NOT NULL)"

        self.__select_settings = "select * from settings where chat_id = %s;"

        self.__get_paged_anime = "SELECT * FROM links WHERE chat_id = %s order by id DESC LIMIT %s OFFSET %s;"
        self.__get_all_anime = "select count(id) from links where chat_id = %s;"
        self.__settings_update_mess_ids = "UPDATE settings SET last_messages = %s," \
                                          "last_pagination = %s WHERE chat_id = %s "

        self.__delete_anime_from_links = "delete from links where chat_id = %s and id = %s"

        self.__get_all_chat_with_anime = "select chat_id from links where  link = %s"

        self.__update_last_anime = "update last_anime set last_anime_in_rss = %s where id = '1'"
        self.__get_last_anime = "SELECT last_anime_in_rss from last_anime"
        self.__insert_first_row = "insert into last_anime (last_anime_in_rss) values ('')"
        self.__clear_last_anime = "update last_anime set last_anime_in_rss = '' where id = '1'"
        self.__count_last_anime = "select count(last_anime_in_rss) from last_anime"

        self.__add_anime_to_db = "insert into links (chat_id, link) values (%s, %s);"

        self.__add_settings = "INSERT INTO settings (chat_id, films_in_one_pagination) " \
                              "VALUES (%s, %s)"
        self.__update_settings = "UPDATE settings SET films_in_one_pagination = %s" \
                                 "WHERE chat_id = %s"

        self.__get_bot_settings = "SELECT * from bot_settings"

        self.__add_bot_settings = "INSERT INTO bot_settings (key, value) " \
                                  "VALUES (%s, %s)"

        self.__update_bot_settings = "UPDATE bot_settings SET value = %s " \
                                     "WHERE key = %s"

        self.__get_active_users = "select chat_id from settings"

        self.__get_download_anime_file_id_by_link = 'select file_id from anime_download where link = %s'

        self.__insert_downloaded_anime = 'insert into anime_download (link, file_id) values (%s, %s)'

        self.__insert_series = 'insert into series (link, name) values (%s, %s)'

        self.__get_series_name_by_link = 'select name from series where link = %s'

        self.__get_anime_link_by_id = "select link from links where id = %s"

    def create_connection(self):
        return psycopg2.connect(
            # host='localhost',
            # user='postgres',
            # password='root',
            # database='animevost_ongoing',

            host=os.getenv('HOST', default=None),
            user=os.getenv('USER', default=None),
            password=os.getenv('PASSWORD', default=None),
            database=os.getenv('DATABASE', default=None),
        )

    def check_or_create_db(self):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __cur = __my_db_connector.cursor()
            __cur.execute(self.__create_db_table_settings)
            __cur.close()

        with __my_db_connector:
            __cur = __my_db_connector.cursor()
            __cur.execute(self.__create_db_table_links)
            __cur.close()

        with __my_db_connector:
            __cur = __my_db_connector.cursor()
            __cur.execute(self.__create_db_table_last_anime)
            __cur.close()

        with __my_db_connector:
            __cur = __my_db_connector.cursor()
            __cur.execute(self.__create_db_table_bot_settings)
            __cur.close()

        with __my_db_connector:
            __cur = __my_db_connector.cursor()
            __cur.execute(self.__create_db_table_anime_download)
            __cur.close()

        with __my_db_connector:
            __cur = __my_db_connector.cursor()
            __cur.execute(self.__create_db_table_series)
            __cur.close()

        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__count_last_anime, )
            all = __con.fetchall()
            __con.close()

        if int(all[0][0]) == 0:
            with __my_db_connector:
                __cur = __my_db_connector.cursor()
                __cur.execute(self.__insert_first_row)
                __cur.close()

    def add_chat(self, chat_id, films_in_one_pagination):
        in_table = self.select_chat_settings(chat_id)
        if len(in_table) > 0:
            self.update_settings(films_in_one_pagination, chat_id)
            return
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__add_settings, (str(chat_id),
                                                str(films_in_one_pagination),
                                                ))
            __my_db_connector.commit()
            __con.close()

    def update_settings(self, films_in_one_pagination, chat_id):
        in_table = self.select_chat_settings(chat_id)
        if len(in_table) == 0:
            return

        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__update_settings, (str(films_in_one_pagination),
                                                   str(chat_id)))
            __my_db_connector.commit()
            __con.close()

    def select_chat_settings(self, chat_id):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__select_settings, (str(chat_id),))
            all = __con.fetchall()
            __con.close()
        return all

    def add_anime_to_db(self, chat_id, link):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__add_anime_to_db, (chat_id, link))
            __my_db_connector.commit()
            __con.close()

    def settings_update_mess_ids(self, chat_id, __message_pagination_ids, __pagination_pages):
        in_table = self.select_chat_settings(chat_id)
        if len(in_table) == 0:
            return

        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__settings_update_mess_ids, (str(__message_pagination_ids), str(__pagination_pages),
                                                            str(chat_id)))
            __my_db_connector.commit()
            __con.close()

    def get_anime_list(self, chat_id, offset, __anime_in_one_pagination):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_paged_anime, (str(chat_id), str(__anime_in_one_pagination), str(offset),))
            all = __con.fetchall()
            __con.close()
        return all

    def get_all_anime_list(self, chat_id):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_all_anime, (str(chat_id),))
            all = __con.fetchall()
            __con.close()
        return all

    def delete_anime_from_links(self, chat_id, anime_id):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__delete_anime_from_links, (str(chat_id), str(anime_id),))
            __my_db_connector.commit()
            __con.close()

    def get_all_chat_with_anime(self, link):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_all_chat_with_anime, (str(link),))
            all = __con.fetchall()
            __con.close()
        return all

    def update_last_anime(self, last_anime):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__update_last_anime, (str(last_anime), ))
            __my_db_connector.commit()
            __con.close()

    def get_last_anime(self,):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_last_anime,)
            all = __con.fetchall()
            __con.close()
        return all

    def clear_last_anime(self):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__clear_last_anime,)
            __my_db_connector.commit()
            __con.close()

    def load_bot_settings(self):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_bot_settings)
            __my_db_connector.commit()
            all = __con.fetchall()
            __con.close()
        return all

    def update_bot_setting(self, key, value):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__update_bot_settings, (key, value, ))
            __my_db_connector.commit()
            __con.close()

    def add_bot_setting(self, key, value):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__add_bot_settings, (key, value, ))
            __my_db_connector.commit()
            __con.close()

    def get_active_users(self):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_active_users)
            __my_db_connector.commit()
            all = __con.fetchall()
            __con.close()
        return all

    def get_anime_file_id_by_link(self, link):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_download_anime_file_id_by_link, (str(link), ))
            __my_db_connector.commit()
            all = __con.fetchall()
            __con.close()
        return all

    def insert_downloaded_anime(self, link, file_id):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__insert_downloaded_anime, (str(link), file_id, ))
            __my_db_connector.commit()
            __con.close()

    def insert_series(self, link, name):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__insert_series, (str(link), name, ))
            __my_db_connector.commit()
            __con.close()

    def get_series_name_by_link(self, link):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_series_name_by_link, (str(link), ))
            __my_db_connector.commit()
            all = __con.fetchall()
            __con.close()
        return all

    def get_anime_link_by_id(self, link_id):
        __my_db_connector = self.create_connection()
        with __my_db_connector:
            __con = __my_db_connector.cursor()
            __con.execute(self.__get_anime_link_by_id, (str(link_id), ))
            __my_db_connector.commit()
            all = __con.fetchall()
            __con.close()
        return all
