# -*- coding:utf-8 -*-
"""
@author: Felix Z
"""
import os
import random
import re
from queue import Queue
import collections
from threading import Thread
import time
import pandas


try:
    import requests
except ImportError:
    os.system('pip install requests')
    import requests

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except ImportError:
    os.system('pip install selenium')
    from selenium.webdriver.common.by import By
    from selenium import webdriver


"""
外链获取：https://link.hhtjim.com/
'https://link.hhtjim.com/163/' + str(id) + '.mp3'
"""


def ua():
    # 用户代理池
    UA_pools = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebkit/537.36 (KHTML, like Gecko)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; en; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7',
        'Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)',
        'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/419 (KHTML, like Gecko, Safari/419.3) Cheshire/1.0.ALPHA',
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36']
    thisua = random.choice(UA_pools)
    return thisua


def get_mp3(name, id, dir):
    url = 'https://link.hhtjim.com/163/' + str(id) + '.mp3'
    response = requests.request("GET", url=url, headers={
        'User-Agent': ua()})
    path = './music/' + dir + '/' + name +'.mp3'
    try:
        with open(path, 'wb') as file:
            for chunk in response.iter_content():
                file.write(chunk)
    except Exception:
        print('song list does not exist, creating new song list named:', dir)
        os.makedirs('./music/' + dir + '/')
        with open(path, 'wb') as file:
            for chunk in response.iter_content():
                file.write(chunk)


class Downloader:
    def __init__(self):
        # start driver
        self.driver = webdriver.Edge()
        self.driver.get('https://music.163.com/#/my')
        self.driver.switch_to.frame('g_iframe')

    def download_all(self, ids, names, songlst):
        for i in range(len(ids)):
            download_que.put((names[i], ids[i], songlst))

    def downlowd_by_indices(self, ids, names, songlst):
        lower = int(input('download songs FROM:'))
        upper = int(input('TO:'))
        for i in range(lower - 1, upper):
            download_que.put((names[i], ids[i], songlst))

    def download_by_names(self, ids, names, songlst):
        counter = 0
        while input('input a new song? Y/N:') == 'Y':
            counter += 1
            inp = input('input song No.' + str(counter) + ':')
            try:
                download_que.put((inp, ids[names.index(inp)], songlst))
            except ValueError:
                print(inp + 'not in the song list')
            except requests.exceptions.ConnectionError:
                print('Error when downloading:', inp)

    def get_songs(self):
        while True:
            print('-'*100)
            input('please log into your account and, enter Y when you do:')
            input('now go to the song list you prefer, enter Y to load the list:')

            # get ids and names
            songs = self.driver.find_elements(By.XPATH, "//table/tbody/tr/td/div/div/div/span/a")
            titles = self.driver.find_elements(By.XPATH, "//table/tbody/tr/td/div/div/div/span/a/b")
            ids = []
            names = []
            for i in range(len(songs)):
                ids.append(re.compile('id=(.*)').findall(songs[i].get_attribute('href'))[0])
                names.append(titles[i].get_attribute('title').replace('\xa0', ' '))
            print('there are '+str(len(ids))+' songs found in the list')
            print(names)
            print(ids)

            usr = input("Download by: (1) names (2) indices (3) Download ALL: ")
            lstname = input('please enter the song list you want to add to:')
            print('-' * 100)
            if usr == '1':
                self.download_by_names(ids, names, lstname)
            if usr == '2':
                self.downlowd_by_indices(ids, names, lstname)
            if usr == '3':
                self.download_all(ids, names, lstname)

    def download_songs(self, que):
        while que.not_empty:
            head = que.get()
            get_mp3(head[0], head[1], head[2])
        print('download que finished')


downloader = Downloader()

download_que = Queue()
Thread(target=downloader.get_songs, args=[]).start()
Thread(target=downloader.download_songs, args=[download_que]).start()
