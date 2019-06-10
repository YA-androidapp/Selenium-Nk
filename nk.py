#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ファイル名設定用
import configparser
import datetime
import os

# Seleniumのドライバ
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# # Seleniumで要素の読み込みを待機するためのパッケージ類
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# BS4
from bs4 import BeautifulSoup
import codecs
import re
import requests

import time

import urllib.parse


currentdirectory = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())

# 設定ファイル読み込み
inifile = configparser.ConfigParser()
inifile.read(os.path.join(currentdirectory, './setting.ini'), 'UTF-8')
nkId = inifile.get('Nk', 'id')
nkPw = inifile.get('Nk', 'pw')

# 定数
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

WAITING_TIME = 10000

# URI
searchTerm = 'ブロックチェーン'
encodedTerm = urllib.parse.quote(searchTerm)
nkBaseUri = 'https://r.nikkei.com/'
nkSigninUri = nkBaseUri + 'login'
nkSearchUri = nkBaseUri + 'search?keyword=' + searchTerm + '&volume=500'


# スクショ保存時のファイル名を生成
def get_filepath():
    now = datetime.datetime.now()
    filename = 'screen_{0:%Y%m%d%H%M%S}.png'.format(now)
    filepath = os.path.join(currentdirectory, filename)
    return filepath


def main():
    with open(LOG_FILEPATH, 'a', encoding='utf-8') as f:
        print('Start: {}'.format(
            datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
        binary = FirefoxBinary(
            'C:\\Program Files\\Mozilla Firefox\\firefox.exe')
        profile = FirefoxProfile(
            'C:\\Users\\y\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\hqterean.default')
        fox = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary,
                                executable_path='C:\\geckodriver\\geckodriver.exe')
        fox.set_page_load_timeout(6000)
        try:
            fox.set_window_size(1280, 720)

            # Sign in
            print('\tnkSigninUri: {} {}'.format(
                nkSigninUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
            fox.get(nkSigninUri)
            time.sleep(2)
            WebDriverWait(fox, WAITING_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'btnM1')))

            clearAndSendKeys(fox, 'LA7010Form01:LA7010Email', nkId)
            clearAndSendKeys(fox, 'LA7010Form01:LA7010Password', nkPw)
            clickClassName(fox, 'btnM1')
            print('btnM1', file=f)

            # https://r.nikkei.com/に遷移するので、フッタが読み込まれるまで待機
            time.sleep(2)

            # 検索
            print('\tnkSearchUri: {} {}'.format(
                nkSearchUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
            fox.get(nkSearchUri)
            time.sleep(2)
            WebDriverWait(fox, WAITING_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'search__result-footer')))
            print('search__result-footer', file=f)
            # time.sleep(2)

            # スクレイピング
            source = fox.page_source
            # BeautifulSoup(source, 'html.parser')
            bs = BeautifulSoup(source, 'lxml')
            print('bs', file=f)
            # print(source, file=f)

            # 該当記事総数
            count = 0
            sel0 = bs.find_all('p', class_='search__result-count')
            for i in sel0:
                print('sel0: {}'.format(i), file=f)
                c = (i.text).replace(',', '')
                if c.isnumeric():
                    count = int(c)
            print('count: {}'.format(count), file=f)

            # 記事毎に取得
            cards = bs.find_all('div', class_='nui-card__main')
            # if count == len(cards):
            #     print('count: {}'.format(count), file=f)
            print('count: {}'.format(len(cards)), file=f)
            for card in cards:
                try:
                    # print(card.text, file=f)
                    title = (card.find_all('h3', attrs={
                        'class': 'nui-card__title'}))[0]
                    uri = (title.find_all('a'))[0].get("href")
                    title = (title.find_all('a'))[0].get("title")
                    pubdate = (card.find_all(
                        'a', attrs={'class': 'nui-card__meta-pubdate'}))[0]
                    pubdate = (pubdate.find_all('time'))[0].get("datetime")
                    print(title, file=f)
                    print('\turi: ' + uri, file=f)
                    print('\tpubdate: ' + pubdate, file=f)

                    # 記事の1ページ目
                    print('\tarticleUri: {} {}'.format(
                        uri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
                    fox.get(uri)

                    # 記事のページ毎に取得
                    while True:
                        try:
                            # ロード完了を待つ
                            time.sleep(2)
                            WebDriverWait(fox, WAITING_TIME).until(
                                EC.presence_of_element_located((By.XPATH, '/html/body')))
                            print('\thtmlbody', file=f)

                            # スクレイピング
                            source2 = fox.page_source
                            # BeautifulSoup(source2, 'html.parser')
                            bs2 = BeautifulSoup(source2, 'lxml')
                            print('\tarticle bs', file=f)

                            try:
                                body = (bs2.find_all('div', attrs={'class': re.compile('cmn-article_text')}))[0] if len(
                                    bs2.find_all('div', attrs={'class': re.compile('cmn-article_text')})) > 0 else (bs2.find_all('div', attrs={
                                        'itemprop': 'articleBody'}))[0] if len(bs2.find_all('div', attrs={
                                            'itemprop': 'articleBody'})) > 0 else ''
                                print('\tbody: {}'.format(
                                    body.replace('\n', '\\n')), file=f)
                            except:
                                pass

                            # li.page_nex_prev があればクリックして次のページへ進む
                            nextpages = bs2.find_all(
                                'ul', attrs={'class': re.compile('pagination_article_detail')})
                            print('\tnextpages: {}'.format(
                                len(nextpages)), file=f)
                            if len(nextpages) > 0:
                                clickLink(fox, '次へ')
                            else:
                                break

                            # time.sleep(600)
                            # break
                        except Exception as e:
                            print(e, file=f)
                except Exception as e:
                    print(e, file=f)

        except Exception as e:
            print(e, file=f)
        finally:
            # ログアウトページ
            try:
                print('\tlogout: {}'.format(
                    datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
                fox.get('https://regist.nikkei.com/ds/etc/accounts/logout')
            except:
                pass

            # 終了時の後片付け
            try:
                fox.close()
                fox.quit()
                print('Done: {}'.format(
                    datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
            except:
                pass


def clickClassName(fox, className):
    fox.find_element_by_class_name(className).click()


def clickId(fox, id):
    fox.find_element_by_id(id).click()


def clickLink(fox, text):
    fox.find_element_by_link_text(text).click()


def clickName(fox, name):
    fox.find_element_by_name(name).click()


def clickSelector(fox, selector):
    fox.find_elements_by_css_selector(selector).click()


def clickXpath(fox, xpath):
    fox.find_element_by_xpath(xpath).click()


def clearAndSendKeys(fox, name, text):
    fox.find_element_by_name(name).clear()
    fox.find_element_by_name(name).send_keys(text)


if __name__ == '__main__':
    main()

# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
