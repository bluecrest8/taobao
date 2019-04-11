import sys
from selenium import webdriver
import time
from scrapinfo import ScrapInfo
from gooddb import GoodsDb
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import configparser
import random


config_file = sys.argv[1]
stop_creep = False
config = configparser.ConfigParser()
config.read(config_file)
db_file = config.get('Default', 'db')
shop_file = config.get('Default', 'shop')
times = config.getint('Default', 'times')
start_page = config.getint('Default', 'start_page')
webpath = config.get('Default', 'driver')
page_count = config.getint('Default', 'page_count')
update_goods = config.getint('Default', 'update_goods')
goods_detail = config.getint('Default', 'goods_detail')
window_count = 15

def my_get(driver1, url, current, total):
    all_windows = driver1.window_handles
    while current < total and current < len(all_windows):
        try:
            driver1.switch_to.window(all_windows[current])
            driver1.get(url)
        except TimeoutException:
            time.sleep(1)
            current = current + 1
            continue
        break
    return current

current_window = 0
db = GoodsDb(db_file)
urllogin = 'https://login.taobao.com/member/login.jhtml'

with open(shop_file, 'r') as f1:
    urlshops = f1.readlines()
for i in range(0, len(urlshops)):
    urlshops[i] = urlshops[i].strip('\r\n') + '&pageNo={}#anchor'

web_option = None
driver = None
m = re.match(r'.*(chromedriver\.exe)', webpath)
if m is not None:
    print(m.groups())
    web_option = webdriver.ChromeOptions()
    #web_option.add_argument('--proxy-server=http://127.0.0.1:8080')
    #web_option.add_argument('--log-level=3')
    driver = webdriver.Chrome(webpath, options=web_option)
m = re.match(r'.*(geckodriver\.exe)', webpath)
if m is not None:
    print(m.groups())
    web_option = webdriver.FirefoxOptions()
    #web_option.add_argument('--proxy-server=http://127.0.0.1:8080')
    #web_option.add_argument('--log-level=3')
    driver = webdriver.Firefox(options=web_option)

for i in range(window_count):
    driver.execute_script('window.open("")')

current_window = my_get(driver, urllogin, current_window, window_count)
login = False
while not login:
    eles = None
    try:
        eles = driver.find_elements_by_tag_name('a')
    except BaseException as e:
        print(e)

    for ee in eles:
        try:
            if ee.text == 'xxxx':#your account name
                login = True
                break
        except BaseException as e:
            print(e)

print("start scraping")
driver.set_page_load_timeout(45)
date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
config.set('Default', 'begin', date)
if times == 0:
    times = int(time.strftime('%Y%m%d', time.localtime(time.time())))
scraper_id = db.update_scrapinfo(date, times)
scrap_infos = []
i = 0
while i < len(urlshops) and stop_creep is False:
    page = 0
    total_page = -1
    pre_total_page = 0
    no_result_new = False
    retry_page = 0
    shop_name = ''
    shop_url = ''
    shop_site = ''
    while stop_creep is False:
        eles = None
        scrap_info = None

        id = ''
        title = ''
        brand = ''
        goods_url = ''
        price = -1
        sold_count = -1
        comment_count = -1
        favourite_count = -1

        if page + start_page > pre_total_page and pre_total_page > 0 or page >= page_count:
            print('page:', page, ',pre_total_page:', pre_total_page)
            break

        if no_result_new is True:
            print('no_result_new is True')
            break

        current_page_url = urlshops[i].format(page + start_page)
        print('page:', page, ',', current_page_url)
        current_window = my_get(driver, current_page_url, current_window, window_count)
        if current_window >= window_count:
            print('error: can not open new window. page:', page)
            stop_creep = True
            break

        if pre_total_page == 0:
            m = re.match(r'(https://([\w\-]+)\.(tmall|taobao)\.com/).*', urlshops[i])
            if m is not None:
                shop_url = m.group(1)
                shop_site = m.group(3)

        try:
            WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div#J_ShopSearchResult')))
        except TimeoutException as e:
            print('Time out div#J_ShopSearchResult')
            continue

        try:
            WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'head > meta[name = "keywords"]')))
        except TimeoutException as e:
            print('Time out head > meta[name = "keywords"]')
            continue

        page_class_name = ''
        try:
            if shop_site == 'taobao':
                page_class_name = 'page-info'
            elif shop_site == 'tmall':
                page_class_name = 'ui-page-s-len'

            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, page_class_name)))
        except TimeoutException as e:
            print('Time out page_class_name:',page_class_name)
            try:
                no_result = driver.find_element_by_css_selector('#J_ShopSearchResult > div > div.no-result-new > p')
                no_result_new = True
                print('no_result_new')
            except BaseException as e:
                print('#J_ShopSearchResult > div > div.no-result-new > p',e)
                pass
            continue

        if pre_total_page == 0:
            try:
                meta = driver.find_element_by_css_selector('head > meta[name = "keywords"]')
                shop_name = meta.get_attribute('content')
            except BaseException as e:
                print('find shop_name ',shop_name, e)
            #print('shop_site:', shop_site,',shop_name:',shop_name, ',shop_url:', shop_url)

        page_info_text = '0/0'
        try:
            page_info = driver.find_element_by_class_name(page_class_name)
            page_info_text = page_info.text
        except BaseException as e:
            print('find page_class_name ',page_class_name, e)

        m = re.match(r'(\d+)/(\d+)', page_info_text)
        if m is not None:
            total_page = int(m.group(2))
            if total_page != pre_total_page and total_page > 0:
                pre_total_page = total_page

        if total_page == 0 and retry_page < 10:
            retry_page = retry_page + 1
            continue
        if retry_page >= 100:
            print('page:', page, ',total_page:', total_page ,',current_page_url:',current_page_url)
            stop_creep = True
            break

        retry_page = 0
        dl_tags = None
        try:
            result = driver.find_element_by_css_selector('div#J_ShopSearchResult')
            dl_tags = result.find_elements_by_tag_name('dl')
        except BaseException as e:
            dl_tags = None
            print('find dl ', e)

        dl_tag = None
        for dl_tag in dl_tags:
            try:
                id = dl_tag.get_attribute('data-id')
            except BaseException as e:
                print('get id ', e)
                continue

            try:
                ele_url = dl_tag.find_element_by_css_selector('dd.detail > a')
                goods_url = ele_url.get_attribute('href')
                title = ele_url.text
            except BaseException as e:
                print('get title ', e)
                goods_url = '-'
                title = '-'

            try:
                ele_price = dl_tag.find_element_by_css_selector('dd.detail > div > div.cprice-area > span.c-price')
                price = float(ele_price.text)
            except BaseException as e:
                price = -1
                print('get price ', e)

            try:
                ele_sold_count = dl_tag.find_element_by_css_selector('dd.detail > div > div.sale-area > span')
                sold_count = int(ele_sold_count.text)
            except BaseException as e:
                sold_count = -1
                print('get sold_count ', e)

            scrap_info = ScrapInfo()
            scrap_info.set_shop_site(shop_site)
            scrap_info.set_shop_url(shop_url)
            scrap_info.set_shop_name(shop_name)
            scrap_info.set_id(id)
            scrap_info.set_goods_url(goods_url)
            scrap_info.set_title(title)
            scrap_info.set_price(price)
            scrap_info.set_sold_count(sold_count)
            scrap_infos.append(scrap_info)

        j = 0
        while j < len(scrap_infos) and stop_creep == False and goods_detail == 1:
            #print('j:',j)
            scrap_info = scrap_infos[j]
            current_window = my_get(driver, scrap_info.goods_url, current_window, window_count)
            if current_window >= window_count:
                print('error: can not open new window. page:', page, ',j:', j)
                stop_creep = True
                break

            try:
                WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'div#page')))
            except BaseException as e:
                print('Time out div#page')
                try:
                    if shop_site == 'taobao':
                        driver.find_element_by_css_selector('div.error-notice-text')
                        j = j + 1
                        print('div.error-notice-text')
                    if shop_site == 'tmall':
                        driver.find_element_by_css_selector('div.errorDetail')
                        j = j + 1
                        print('div.errorDetail')
                except NoSuchElementException as e:
                    print('div.error',e)
                    pass
                except BaseException as e:
                    print(e)
                continue

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'a > em.J_ReviewsCount')))
            except TimeoutException as e:
                print('a > em.J_ReviewsCount')
                pass

            pg = None
            try:
                pg = driver.find_element_by_css_selector('div#page')
            except BaseException as e:
                print('find div#page', e)
                continue

            lis = []
            attr = None
            brand = ''
            try:
                if shop_site == 'taobao':
                    attr = pg.find_element_by_css_selector('ul.attributes-list')
                elif shop_site == 'tmall':
                    attr = pg.find_element_by_css_selector('ul#J_AttrUL')
                if attr is not None:
                    lis = attr.find_elements_by_tag_name('li')
            except BaseException as e:
                print(e)
                brand = '-'
            for li in lis:
                brand = brand + '|' + li.text
            scrap_info.set_brand(brand)

            comment_count = -1
            try:
                comment = pg.find_element_by_css_selector('a > em.J_ReviewsCount')
                comment_count = int(comment.text)
            except BaseException as er:
                print('get comment ', er)
            scrap_info.set_comment_count(comment_count)

            favourite = None
            favourite_count = -1
            try:
                if shop_site == 'taobao':
                    favourite = pg.find_element_by_css_selector('a > em.J_FavCount')
                elif shop_site == 'tmall':
                    favourite = pg.find_element_by_css_selector('span#J_CollectCount')
                if favourite is not None:
                    m = re.match(r'.*?(\d+)(\.*).*', favourite.text)
                    if m is not None:
                        if m.group(2) == '...':
                            favourite_count = int(m.group(1))*10000+9999
                        else:
                            favourite_count = int(m.group(1))
            except BaseException as e:
                print('get favourite_count ',e)
            scrap_info.set_favourite_count(favourite_count)
            j = j + 1

        for scrap_info in scrap_infos:
            db.store_shop(scrap_info)
            db.store_goods(scrap_info, update_goods)
            db.store_salesinfo(scrap_info, scraper_id)
        scrap_infos.clear()
        config.set('Default', 'current_page', str(page))
        page = page + 1
    i = i + 1
print("end scraping")
end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
driver.save_screenshot(end+'.png')
db.update_end(scraper_id, end)
config.set('Default', 'end', end)
config.write(open(config_file, 'w'))
input('Press Enter to close')
driver.quit()

