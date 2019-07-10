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

import time

import urllib.parse


currentdirectory = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())

# 定数
DATA_FILEPATH = os.path.join(
    currentdirectory, 'tk'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

WAITING_TIME = 10000

# URI
searchTerm = 'ブロックチェーン'
encodedTerm = urllib.parse.quote(searchTerm)
tkBaseUri = 'https://toyokeizai.net'
tkSearchUri = tkBaseUri + '/search?fulltext=' + searchTerm


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

                # 検索
                print('\ttkSearchUri: {} {}'.format(
                    tkSearchUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                fox.get(tkSearchUri)
                time.sleep(2)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'current')))
                print('current', file=logfile, flush=True)
                time.sleep(1)

                # スクレイピング
                source = fox.page_source
                # BeautifulSoup(source, 'html.parser')
                bs = BeautifulSoup(source, 'lxml')
                print('bs', file=logfile, flush=True)
                # print(source, file=logfile, flush=True)

                # 該当記事総数
                sel0 = bs.find_all('span', class_='page')
                lastPage = 0
                for i in sel0:
                    # print('sel0: {}'.format(i), file=logfile, flush=True)
                    c = (i.a.text)
                    if c.isnumeric():
                        count = int(c)
                        if count > lastPage:
                            lastPage = count
                print('lastPage: {}'.format(lastPage),
                      file=logfile, flush=True)

                # ページ毎に取得
                for pageNum in range(2, lastPage):
                    try:
                        # print(bs.text, file=logfile, flush=True)
                        listclass = bs.find_all('div', attrs={
                            'class': 'article-list'})[0]
                        # print('listclass: {}'.format(listclass), file=logfile, flush=True)

                        titleclass = listclass.find_all('li')
                        # print('titleclass[0]: {}'.format(
                        #     titleclass[0]), file=logfile, flush=True)

                        # 記事毎に取得
                        for article in titleclass:
                            # 明示的に初期化
                            title = ''
                            uri = ''
                            pubdate = ''
                            body = ''

                            try:
                                # print('article: {}'.format(article.text),
                                #       file=logfile, flush=True)

                                uri = ''
                                try:
                                    uri_a = article.find_all('a')
                                except:
                                    uri_a = None
                                if len(uri_a) > 0:
                                    uri = uri_a[0].get("href")
                                if not uri.startswith(tkBaseUri):
                                    uri = tkBaseUri + uri

                                title = ''
                                try:
                                    column_main_ttl = article.find_all(
                                        'span', attrs={'class': 'column-main-ttl'})
                                except:
                                    column_main_ttl = None
                                if len(column_main_ttl) > 0:
                                    title = column_main_ttl[0].text
                                else:
                                    title = ''

                                # pubdate = ''
                                # try:
                                #     span_date = article.find_all(
                                #         'span', attrs={'class': 'date'})
                                # except:
                                #     span_date = None
                                # if len(span_date) > 0:
                                #     pubdate = span_date[0].text
                                # else:
                                #     pubdate = ''

                                print('title: {}'.format(title),
                                      file=logfile, flush=True)
                                print('\turi: {}'.format(uri),
                                      file=logfile, flush=True)
                                # print('\tpubdate: {}'.format(pubdate),
                                #       file=logfile, flush=True)

                                # ロード完了を待つ
                                fox.get(uri)
                                time.sleep(2)
                                WebDriverWait(fox, WAITING_TIME).until(
                                    EC.presence_of_element_located((By.XPATH, '/html/body')))
                                print('\thtmlbody', file=logfile, flush=True)

                                # スクレイピング
                                source2 = fox.page_source
                                # BeautifulSoup(source2, 'html.parser')
                                bs2 = BeautifulSoup(source2, 'lxml')
                                print('\tarticle bs', file=logfile, flush=True)

                                try:
                                    article_body_inner = bs2.find_all(
                                        'div', attrs={'id': 'article-body-inner'})
                                    # print('article_body_inner: {}'.format(
                                    #     article_body_inner))
                                except:
                                    article_body_inner = None

                                if len(article_body_inner) > 0:
                                    body = article_body_inner[0].text
                                    # print('article_body_inner[0]: {}'.format(
                                    #     article_body_inner[0]))
                                else:
                                    body = ''

                                body = body.strip().replace('\n', '\\n')
                                print('\t\tbody: {}'.format(body),
                                      file=logfile, flush=True)

                                # if pubdate == '':
                                pubdate = ''
                                try:
                                    span_date = article.find_all(
                                        'span', attrs={'class': 'date'})
                                except:
                                    span_date = None
                                if len(span_date) > 0:
                                    pubdate = span_date[0].text
                                else:
                                    pubdate = ''
                                print('\tpubdate: {}'.format(pubdate),
                                      file=logfile, flush=True)

                                author = ''
                                try:
                                    div_author = article.find_all(
                                        'div', attrs={'class': 'author'})
                                except:
                                    div_author = None
                                if len(div_author) > 0:
                                    author = div_author[0].text.replace(
                                        '\n', '\\n')
                                else:
                                    author = ''
                                print('\tauthor: {}'.format(author),
                                      file=logfile, flush=True)

                                # データファイルに出力
                                print('{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(
                                    title, pubdate, uri, author, body), file=datafile, flush=True)

                            except Exception as e:
                                print(e, file=logfile, flush=True)

                        # 次のページへ進む
                        try:
                            fox.get(tkSearchUri + '&page={}'.format(pageNum))
                            time.sleep(2)
                            WebDriverWait(fox, WAITING_TIME).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'current')))
                            print('current', file=logfile, flush=True)
                            time.sleep(1)

                            # スクレイピング
                            source = fox.page_source
                            # BeautifulSoup(source, 'html.parser')
                            bs = BeautifulSoup(source, 'lxml')
                            print('bs', file=logfile, flush=True)
                            # print(source, file=logfile, flush=True)

                        except Exception as e:
                            print(e, file=logfile, flush=True)

                        # time.sleep(600)
                        # break
                    except Exception as e:
                        print(e, file=logfile, flush=True)

            except Exception as e:
                print(e, file=logfile, flush=True)
            finally:
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
