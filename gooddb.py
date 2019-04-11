import sqlite3
from scrapinfo import ScrapInfo
import datetime

class GoodsDb:
    def __init__(self, file_name):
        self.db = None
        self.file_name = file_name
        try:
            self.db = sqlite3.connect(self.file_name)
            #self.db = sqlite3.connect(':memory:')
            cur = self.db.cursor()
            cur.execute('''create table if not exists goods (goods_id integer not null, \
                shop_id integer null, \
                id text null, \
                title text null, \
                brand text null, \
                good_url text null, \
                constraint PK_GOODS primary key (goods_id)) ''')

            cur.execute('''create unique index if not exists goods_PK on goods ( goods_id ASC)''')
            cur.execute('''create index if not exists Relationship_1_FK on goods ( shop_id ASC)''')
            cur.execute('''create table if not exists salesinfo (salesinfo_id integer not null, \
                goods_id integer null, \
                scraper_id integer null, \
                price double null, \
                sold_count integer null, \
                comment_count integer null, \
                favourite_count integer null, \
                constraint PK_SALESINFO primary key (salesinfo_id)) ''')
            cur.execute('''create unique index if not exists salesinfo_PK on salesinfo ( salesinfo_id ASC)''')
            cur.execute('''create index if not exists Relationship_2_FK on salesinfo ( goods_id ASC)''')
            cur.execute('''create index if not exists Relationship_3_FK on salesinfo ( scraper_id ASC)''')
            cur.execute('''create table if not exists scraper (scraper_id integer not null, \
                times integer null, \
                date datetime null, \
                end datetime null, \
                constraint PK_SCRAPER primary key (scraper_id)) ''')
            cur.execute('''create unique index if not exists scraper_PK on scraper ( scraper_id ASC)''')
            cur.execute('''create table if not exists shop (shop_id integer not null, \
                shop_name text null, \
                shop_url text null, \
                shop_site text null, \
                constraint PK_SHOP primary key (shop_id)) ''')
            cur.execute('''create unique index if not exists shop_PK on shop ( shop_id ASC)''')
            cur.close()
        except BaseException as e:
            print(e)

    def store_shop(self, item:ScrapInfo):
        shop_name = item.shop_name
        shop_url = item.shop_url
        shop_site = item.shop_site
        try:
            cur = self.db.cursor()
            cur.execute('''select * from shop where shop_url = ?''', (shop_url,))
            rows = cur.fetchall()
            if len(rows) <= 0:
                cur.execute('''insert into shop (shop_name, shop_url, shop_site) \
                values(?, ?, ?)''', (shop_name, shop_url, shop_site,))
                self.db.commit()
                cur.execute('''select * from shop where shop_url = ?''', (shop_url,))
                rows = cur.fetchall()
                if len(rows) > 0:
                    item.set_shop_id(rows[0][0])
            else:
                item.set_shop_id(rows[0][0])
            cur.close()
        except BaseException as e:
            print(e)

    def store_goods(self, item:ScrapInfo, update_goods):
        shop_id = item.shop_id
        id = item.id
        title = item.title
        brand = item.brand
        good_url = item.goods_url
        try:
            cur = self.db.cursor()
            cur.execute('''select * from goods where id = ?''', (id,))
            rows = cur.fetchall()
            if len(rows) <= 0:
                cur.execute('''insert into goods (shop_id, id, title, brand, good_url) \
                values(?, ?, ?, ?, ?)''', (shop_id, id, title, brand, good_url))
                self.db.commit()
                cur.execute('''select * from goods where id = ?''', (id,))
                rows = cur.fetchall()
                if len(rows) > 0:
                    item.set_goods_id(rows[0][0])
            else:
                item.set_goods_id(rows[0][0])
                if update_goods == 1:
                    cur.execute('''update goods set title = ?, brand = ?, good_url = ? where id = ?''',
                                (title, brand, good_url, id))
                    self.db.commit()
            cur.close()
        except BaseException as e:
            print(e)

    def store_salesinfo(self, item:ScrapInfo, scraper_id):
        goods_id = item.goods_id
        price = item.price
        sold_count = item.sold_count
        comment_count = item.comment_count
        favourite_count = item.favourite_count
        try:
            cur = self.db.cursor()
            cur.execute('''select * from salesinfo where goods_id = ? and scraper_id = ?''', (goods_id, scraper_id,))
            rows = cur.fetchall()
            if len(rows) <= 0:
                cur.execute('''insert into salesinfo (goods_id, scraper_id, price, sold_count, comment_count, favourite_count) \
                values(?, ?, ?, ?, ?, ?)''', (goods_id, scraper_id, price, sold_count, comment_count, favourite_count))
                self.db.commit()
                cur.execute('''select * from salesinfo where goods_id = ? and scraper_id = ?''', (goods_id, scraper_id,))
                rows = cur.fetchall()
                if len(rows) > 0:
                    item.set_salesinfo_id(rows[0][0])
            else:
                item.set_salesinfo_id(rows[0][0])
            cur.close()
        except BaseException as e:
            print(e)

    def update_scrapinfo(self, date, times):
        try:
            cur = self.db.cursor()
            cur.execute('''select * from scraper where times = ?''', (times,))
            rows = cur.fetchall()
            if len(rows) <= 0:
                cur.execute('''insert into scraper (date, times) values(?, ?)''', (date, times,))
                self.db.commit()
                cur.execute('''select * from scraper where times = ?''', (times,))
                rows = cur.fetchall()
                if len(rows) > 0:
                    return rows[0][0]
            else:
                return  rows[0][0]
            cur.close()
        except BaseException as e:
            print(e)
        return -1

    def update_end(self, scraper_id, end):
        try:
            cur = self.db.cursor()
            cur.execute('''select * from scraper where scraper_id = ?''', (scraper_id,))
            rows = cur.fetchall()
            if len(rows) > 0:
                cur.execute('''update scraper set end = ? where scraper_id = ?''', (end, scraper_id))
                self.db.commit()
            cur.close()
        except BaseException as e:
            print(e)

    def get_goods_url_by_goods_id(self, scrap_info: ScrapInfo):
        try:
            cur = self.db.cursor()
            cur.execute('''select * from goods where goods_id = ?''', (scrap_info.goods_id,))
            rows = cur.fetchall()
            if len(rows) > 0:
                scrap_info.goods_url = rows[0][5]
            cur.close()
        except BaseException as e:
            print(e)

    def get_goods_by_id(self, scrap_info: ScrapInfo):
        try:
            cur = self.db.cursor()
            cur.execute('''select goods_id, title, brand, good_url from goods where id = ?''', (scrap_info.id,))
            rows = cur.fetchall()
            if len(rows) > 0:
                scrap_info.goods_id = rows[0][0]
                scrap_info.title = rows[0][1]
                scrap_info.brand = rows[0][2]
                scrap_info.goods_url = rows[0][3]
            cur.close()
        except BaseException as e:
            print(e)

    def update_comment_count(self, scrap_info):
        try:
            cur = self.db.cursor()
            cur.execute('''update salesinfo set comment_count = ? where goods_id = ?''', (scrap_info.comment_count,scrap_info.goods_id))
            self.db.commit()
            cur.close()
        except BaseException as e:
            print(e)

    def update_favourite_count(self, scrap_info):
        try:
            cur = self.db.cursor()
            cur.execute('''update salesinfo set favourite_count = ? where goods_id = ?''', (scrap_info.favourite_count, scrap_info.goods_id))
            self.db.commit()
            cur.close()
        except BaseException as e:
            print(e)

    def update_brand(self, scrap_info):
        try:
            cur = self.db.cursor()
            cur.execute('''update salesinfo set brand = ? where goods_id = ?''', (scrap_info.brand, scrap_info.goods_id))
            self.db.commit()
            cur.close()
        except BaseException as e:
            print(e)