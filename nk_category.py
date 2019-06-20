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

# Get json
import json
import urllib.request

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
DATA_FILEPATH = os.path.join(
    currentdirectory, 'nkc'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

WAITING_TIME = 10000

# URI
nkRBaseUri = 'https://r.nikkei.com/'
nkSigninUri = nkRBaseUri + 'login'

nkBaseUri = 'https://www.nikkei.com'
nkcategoryUris = [
    nkBaseUri + '/economy/archive/',
    nkBaseUri + '/business/archive/',
    nkBaseUri + '/markets/archive/',
    nkBaseUri + '/technology/archive/',
    # nkBaseUri + '/international/archive/',
    # nkBaseUri + '/sports/archive/',
    # nkBaseUri + '/society/archive/',
    # nkBaseUri + '/local/archive/',
    # nkBaseUri + '/opinion/archive/',
    # nkBaseUri + '/culture/archive/'
]

# カテゴリ毎に、取得するページ数
MAX_PAGE_PER_CATEGORY = 2


# スクショ保存時のファイル名を生成
def get_filepath():
    now = datetime.datetime.now()
    filename = 'screen_{0:%Y%m%d%H%M%S}.png'.format(now)
    filepath = os.path.join(currentdirectory, filename)
    return filepath


def main():
    with open(DATA_FILEPATH, 'a', encoding='utf-8') as datafile:
        with open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
            print('Start: {}'.format(
                datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
            binary = FirefoxBinary(
                'C:\\Program Files\\Mozilla Firefox\\firefox.exe')
            profile = FirefoxProfile(
                'C:\\Users\\y\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\hqterean.default')
            fox = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary,
                                    executable_path='C:\\geckodriver\\geckodriver.exe')
            fox.set_page_load_timeout(6000)
            try:
                fox.set_window_size(1280, 720)

                # # Sign in
                # print('\tnkSigninUri: {} {}'.format(
                #     nkSigninUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                # fox.get(nkSigninUri)
                # time.sleep(3)
                # WebDriverWait(fox, WAITING_TIME).until(
                #     EC.presence_of_element_located((By.CLASS_NAME, 'btnM1')))

                # clearAndSendKeys(fox, 'LA7010Form01:LA7010Email', nkId)
                # clearAndSendKeys(fox, 'LA7010Form01:LA7010Password', nkPw)
                # clickClassName(fox, 'btnM1')
                # print('btnM1', file=logfile, flush=True)

                # # https://r.nikkei.com/に遷移するので、フッタが読み込まれるまで待機
                # time.sleep(3)
                # # Sign in

                # カテゴリごとに記事一覧を取得
                for nkCatUri in nkcategoryUris:
                    print('\tnkCatUri: {} {}'.format(
                        nkCatUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

                    category = (nkCatUri.split(nkBaseUri + '/')[1]).split('/archive/')[0]

                    fox.get(nkCatUri)
                    time.sleep(3)
                    WebDriverWait(fox, WAITING_TIME).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'm-pageNation')))
                    print('m-pageNation', file=logfile, flush=True)
                    # time.sleep(3)

                    for i in range(0, MAX_PAGE_PER_CATEGORY):
                        print('i: {}'.format(i), file=logfile, flush=True)

                        # スクレイピング
                        if i > 0:
                            nkCatUri = nkCatUri.split(
                                '?bn=')[0] + '?bn='+str(i)+'1'
                            print('\tnkCatUri: {} {}'.format(
                                nkCatUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                            fox.get(nkCatUri)
                            time.sleep(3)
                            WebDriverWait(fox, WAITING_TIME).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'm-pageNation')))
                            print('m-pageNation', file=logfile, flush=True)

                        source = fox.page_source
                        # BeautifulSoup(source, 'html.parser')
                        bs = BeautifulSoup(source, 'lxml')
                        print('bs', file=logfile, flush=True)
                        # print(source, file=logfile, flush=True)

                        # 記事毎に取得
                        contents = (bs.find_all('div', id='CONTENTS_MAIN'))
                        print('i: {} ; contents: {}'.format(i, len(contents)),
                              file=logfile, flush=True)
                        if len(contents) == 0:
                            continue
                        cards = contents[0].find_all('div', class_='m-miM09')
                        print('i: {} ; count: {}'.format(i, len(cards)),
                              file=logfile, flush=True)

                        for card in cards:
                            # 明示的に初期化
                            title = ''
                            uri = ''
                            pubdate = ''
                            body = ''

                            try:
                                # print(card.text, file=logfile, flush=True)
                                titleclass = (card.find_all('h3', attrs={
                                    'class': 'm-miM09_title'}))[0]
                                uri = (titleclass.find_all('a'))[0].get("href")
                                uri = nkBaseUri + uri
                                title = (titleclass.find_all('span', attrs={
                                         'class': 'm-miM09_titleL'}))[0].text
                                pubdate = (card.find_all('span', attrs={
                                           'class': 'm-miM09_date'}))[0].text
                                print('\ttitle: ' + title,
                                      file=logfile, flush=True)
                                print('\turi: ' + uri, file=logfile, flush=True)
                                print('\tpubdate: ' + pubdate,
                                      file=logfile, flush=True)

                                # 記事の1ページ目
                                print('\tarticleUri: {} {}'.format(
                                    uri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                                fox.get(uri)

                                # 記事のページ毎に取得
                                while True:
                                    try:
                                        # ロード完了を待つ
                                        time.sleep(3)
                                        WebDriverWait(fox, WAITING_TIME).until(
                                            EC.presence_of_element_located((By.XPATH, '/html/body')))
                                        print('\thtmlbody',
                                              file=logfile, flush=True)

                                        # スクレイピング
                                        source2 = fox.page_source
                                        # BeautifulSoup(source2, 'html.parser')
                                        bs2 = BeautifulSoup(source2, 'lxml')
                                        print('\tarticle bs',
                                              file=logfile, flush=True)

                                        try:
                                            bodyclass = ''
                                            try:
                                                cmn_article_text = bs2.find_all(
                                                    'div', attrs={'class': re.compile('.*?cmn-article_text.*?')})
                                                # print('cmn_article_text: {}'.format(
                                                #     cmn_article_text))
                                            except:
                                                cmn_article_text = None

                                            if len(cmn_article_text) > 0:
                                                bodyclass = cmn_article_text[0].text
                                                # print('cmn_article_text[0]: {}'.format(
                                                #     cmn_article_text[0]))
                                            else:
                                                try:
                                                    articleBody = bs2.find_all(
                                                        'div', attrs={'itemprop': 'articleBody'})
                                                    # print('articleBody: {}'.format(
                                                    #     articleBody))
                                                except:
                                                    articleBody = None

                                                if len(articleBody) > 0:
                                                    bodyclass = articleBody[0].text
                                                    # print('articleBody[0]: {}'.format(
                                                    #     articleBody[0]))
                                                else:
                                                    bodyclass = ''

                                            print('\tbodyclass: {}'.format(
                                                bodyclass), file=logfile, flush=True)
                                            body += bodyclass.strip().replace('\n', '\\n')
                                            # print('\t\tbody: {}'.format(body),
                                            #       file=logfile, flush=True)
                                        except Exception as e:
                                            print(e, file=logfile, flush=True)

                                        # li.page_nex_prev があればクリックして次のページへ進む
                                        nextpages = bs2.find_all(
                                            'ul', attrs={'class': re.compile('.*?pagination_article_detail.*?')})
                                        print('\tnextpages: {} {}'.format(
                                            len(nextpages), nextpages), file=logfile, flush=True)
                                        if len(nextpages) > 0:
                                            try:
                                                clickLink(fox, '次へ')
                                            except:
                                                break  # Message: Unable to locate element: 次へ
                                        else:
                                            break

                                        # time.sleep(600)
                                        # break
                                    except Exception as e:
                                        print(e, file=logfile, flush=True)
                                        break

                                # データファイルに出力
                                print('{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(
                                    category, title, pubdate, uri, body), file=datafile, flush=True)
                            except Exception as e:
                                print(e, file=logfile, flush=True)

            except Exception as e:
                print(e, file=logfile, flush=True)
            finally:
                # ログアウトページ
                try:
                    print('\tlogout: {}'.format(
                        datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                    fox.get('https://regist.nikkei.com/ds/etc/accounts/logout')
                except:
                    pass

                # 終了時の後片付け
                try:
                    fox.close()
                    fox.quit()
                    print('Done: {}'.format(
                        datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
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
