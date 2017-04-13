import logging
import os

from urllib.request import urlopen

import io

from bs4 import BeautifulSoup

from selenium import webdriver

from apps import app

try:
    from PIL import Image
except:
    raise ImportError('PIL 필요')


def _crawl_to_soup(domain, url):
    """
    crawling 후 soup로 바꿔준다.
    javascript care
    :param url:
    :return:
    """
    if url is None or domain is None:
        app.logger.warning('crawl fail. url과 domain은 설정되어야 합니다.')
        return None
    path = os.path.join(domain, url)
    # resp = urlopen(path)

    chrome_driver = "/usr/local/bin/chromedriver"
    # selenium.webdriver - 자바스크립트 위해
    driver = webdriver.Chrome(chrome_driver)
    driver.get(path)

    # html parsing
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    # soup = BeautifulSoup(resp, 'html.parser')

    driver.quit()
    return soup


def _crawl_image(image_src_list):
    if image_src_list is None:
        return None


def crawl_wemakeprice_detail(url):
    domain = 'http://wemakeprice.com/'
    soup = _crawl_to_soup(domain, url)

    # view-selected 클래스가 있을때 파싱해도 된다.
    can_crawl = soup.find('div', class_='view-selected')

    if not can_crawl:
        print("파싱할 수 없습니다. 제품에 셀렉트 옵션이 있습니다. \n%s, %s" % (domain, url))
        return None

    product_header = soup.find('div', class_='deal_info')

    prod_img_src = []  # 이미지 저장할 리스트
    img_tags = product_header.find('div', class_='roll').find_all('li')
    for img_tag in img_tags:
        prod_img_src.append(img_tag.find('img')['src'])

    prod_title = soup.find('div', class_='section-header').find('h2').string

    prod_price = product_header.find('li', class_='sale').find('span', class_='num').string.replace(',', '')

    prod_attribute = []

    attribute_tags = soup.find('div', class_='wrap_product_info')

    return dict(images=prod_img_src)


def crawl_coupang(url):
    """
    :param url:
    :return:
    """
    if url is None:
        app.logger.warning('coupang crawl failed.')
        return None

    soup = _crawl_to_soup(url)

    img_tags = soup.find_all('div', class_='prod-image__item')

    prod_tag = soup.find('div', class_='prod-buy')

    title = prod_tag.find('h2', class_='prod-buy-header__title').text
    category_name = prod_tag.find('span', class_='top-category-link').text
    price = prod_tag.find('span', id='totalPrice').text

    attribute_tags = prod_tag.find_all('li', class_='prod-attr-item')

    print(attribute_tags)
    for attribute_tag in attribute_tags:
        for string in attribute_tag.stripped_strings:
            print(string)
    print('------------------------')
    for attribute_tag in attribute_tags:
        for string in attribute_tag.strings:
            print(string)
    print('------------------------')
    for attribute_tag in attribute_tags:
        print(attribute_tag.contents)

    prd_imgs = []

    for img_tag in img_tags:
        img_src = img_tag['data-detail-img-src']
        prd_imgs.append(img_src)


def crawling(url=None):
    try:
        if url is None:
            raise ImportError
    except:
        logging.debug('crawling을 할 수 없습니다.\nurl을 입력해주십시요.')

    chromedriver = "/usr/local/bin/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get(url=url)

    # html parsing
    html = driver.page_source

    # Beautiful soup Instance
    soup = BeautifulSoup(html, 'html.parser')
    print(type(soup))

    # image tag
    image_tags = soup.find_all('div', class_='prod-image__item')

    # 이밎 관련 태그로부터 이미지를 가져온다.
    for image_tag in image_tags:
        image_src = image_tag['data-detail-img-src']
        img_src = urlopen(image_src)

        # print(img_src.read())
        image = io.BytesIO(img_src.read())
        # 이미지 오픈
        with Image.open(image) as image:
            image.show()

    # Image.open(img_src.read()).show()
    # with Image.open(img_src.read(),'r') as image:
    #     image.show()

    driver.quit()
    return image_tags
    # res = urlopen(url).read().decode('utf-8')

    # soup = BeautifulSoup(res,'html.parser')
    # print(res.read().decode('utf-8'))
    # code = requests.get(url=url)
    # text = code.text

    # prod_title = soup.find('div', class_='prod-atf')
    # print(prod_title)

    # return prod_title

    # coupang: prod-atf - prod_detail <header>
    # coupang: prod-atf
    # coupang: prod-atf
