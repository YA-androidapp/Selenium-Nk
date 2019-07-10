#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

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
    currentdirectory, 'nk'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

WAITING_TIME = 10000

# URI
searchTerm = 'ブロックチェーン'
encodedTerm = urllib.parse.quote(searchTerm)
nkBaseUri = 'https://r.nikkei.com/'
nkSigninUri = nkBaseUri + 'login'
nkSearchUri = nkBaseUri + 'search?keyword=' + encodedTerm + '&volume=200'


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

                # Sign in
                print('\tnkSigninUri: {} {}'.format(
                    nkSigninUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                fox.get(nkSigninUri)
                time.sleep(3)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'btnM1')))

                clearAndSendKeys(fox, 'LA7010Form01:LA7010Email', nkId)
                clearAndSendKeys(fox, 'LA7010Form01:LA7010Password', nkPw)
                clickClassName(fox, 'btnM1')
                print('btnM1', file=logfile, flush=True)

                # https://r.nikkei.com/に遷移するので、フッタが読み込まれるまで待機
                time.sleep(3)

                # 検索
                print('\tnkSearchUri: {} {}'.format(
                    nkSearchUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                fox.get(nkSearchUri)
                time.sleep(3)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'search__result-footer')))
                print('search__result-footer', file=logfile, flush=True)
                # time.sleep(3)

                # スクレイピング
                source = fox.page_source
                # BeautifulSoup(source, 'html.parser')
                bs = BeautifulSoup(source, 'lxml')
                print('bs', file=logfile, flush=True)
                # print(source, file=logfile, flush=True)

                # 該当記事総数
                count = 0
                sel0 = bs.find_all('p', class_='search__result-count')
                for i in sel0:
                    print('sel0: {}'.format(i), file=logfile, flush=True)
                    c = (i.text).replace(',', '')
                    if c.isnumeric():
                        count = int(c)
                print('count: {}'.format(count), file=logfile, flush=True)

                # 200件以前と201件以降で取得方法が若干異なる
                maxpage = -((-1 * count) // 200)
                for i in range(0, maxpage):
                    print('i: {}'.format(i), file=logfile, flush=True)

                    if i > 0:
                        nkJsonUri = nkBaseUri + '.resources/search/partials?keyword=' + \
                            encodedTerm + '&offset=' + \
                            str(200*i) + '&volume=200'
                        print('nkJsonUri: {}'.format(nkJsonUri),
                              file=logfile, flush=True)
                        try:
                            res = urllib.request.urlopen(nkJsonUri)
                            print('res: {}'.format(nkJsonUri),file=logfile, flush=True)
                            data = json.loads(res.read().decode('utf-8'))
                            print('data: {}'.format(nkJsonUri),file=logfile, flush=True)
                            source = data['html']
                            print('source: {}'.format(nkJsonUri),file=logfile, flush=True)
                            bs = BeautifulSoup(source, 'lxml')
                            print('bs {}'.format(i), file=logfile, flush=True)
                        except urllib.error.HTTPError as e:
                            print(e, file=logfile, flush=True)
                            continue
                        except json.JSONDecodeError as e:
                            print(e, file=logfile, flush=True)
                            continue

                    # 記事毎に取得
                    cards = bs.find_all('div', class_='nui-card__main')
                    # if count == len(cards):
                    #     print('count: {}'.format(count), file=logfile, flush=True)
                    print('count: {}'.format(len(cards)),
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
                                'class': 'nui-card__title'}))[0]
                            uri = (titleclass.find_all('a'))[0].get("href")
                            title = (titleclass.find_all('a'))[0].get("title")
                            pubdate = (card.find_all(
                                'a', attrs={'class': 'nui-card__meta-pubdate'}))[0]
                            pubdate = (pubdate.find_all('time'))[
                                0].get("datetime")
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
                                    print('\thtmlbody', file=logfile, flush=True)

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
                            print('{}\t\t{}\t\t{}\t\t{}'.format(
                                title, pubdate, uri, body), file=datafile, flush=True)
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
