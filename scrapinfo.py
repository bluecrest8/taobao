
class ScrapInfo:
    def __init__(self):
        self.shop_id = -1
        self.shop_name = ''
        self.shop_url = ''
        self.shop_site = ''
        self.goods_id = -1
        self.id = ''
        self.title = ''
        self.brand = ''
        self.goods_url = ''
        self.salesinfo_id = -1
        self.price = 0.0
        self.sold_count = -1
        self.comment_count = -1
        self.favourite_count = -1
    def __str__(self):
        return 'shop_id:'+str(self.shop_id) + \
            ',shop_name:'+self.shop_name + \
            ',shop_url:'+self.shop_url + \
            ',shop_site:'+self.shop_site + \
            ',goods_id:' + str(self.goods_id) + \
            ',id:' + self.id + \
            ',title:' + self.title + \
            ',brand:'+self.brand + \
            ',goods_url:' + self.goods_url + \
            ',salesinfo_id:' + str(self.salesinfo_id) + \
            ',price:'+str(self.price) + \
            ',sold_count:'+str(self.sold_count) + \
            ',comment_count:'+str(self.comment_count) + \
            ',favourite_count:'+str(self.favourite_count)

    def set_shop_id(self, shop_id):
        self.shop_id = shop_id

    def set_shop_name(self, shop_name):
        self.shop_name = shop_name

    def set_shop_url(self, shop_url):
        self.shop_url = shop_url

    def set_shop_site(self, shop_site):
        self.shop_site = shop_site

    def set_goods_id(self, goods_id):
        self.goods_id = goods_id

    def set_id(self, id):
        self.id = id

    def set_title(self, title):
        self.title = title

    def set_brand(self, brand):
        self.brand = brand

    def set_goods_url(self, goods_url):
        self.goods_url = goods_url

    def set_salesinfo_id(self, salesinfo_id):
        self.salesinfo_id = salesinfo_id

    def set_price(self, price):
        self.price = price

    def set_sold_count(self, sold_count):
        self.sold_count = sold_count

    def set_comment_count(self, comment_count):
        self.comment_count = comment_count

    def set_favourite_count(self, favourite_count):
        self.favourite_count = favourite_count