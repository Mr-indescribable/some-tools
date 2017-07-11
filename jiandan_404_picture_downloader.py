#!/usr/bin/env python3
#coding:utf-8

import os
import re
import sys
import time
import random
import argparse
from string import ascii_uppercase, ascii_lowercase, digits

import requests


def randkey(size=12, chars=None):
    chars = chars or (ascii_uppercase + ascii_lowercase + digits)
    return ''.join(random.choice(chars) for i in range(size))


class Jiandan404Page(object):
    html = None
    pic_url = None

    def __init__(self, html):
        self.html = html
        self.pic_url = self.get_pic_url(self.html)

    def __repr__(self):
        return self.html

    def get_pic_url(self, html):
        try:
            return re.findall(r'(?<=img\ src\=").*(?="\ \/)', html)[0]
        except IndexError:
            return None


class Jiandan404PicDownloader(object):
    pics = []
    pic_dir = None

    base_url = 'http://jandan.net'
    headers_jiandan = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'jandan.net',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +\
                    '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
            }

    paths = ['/', '/new/', '/tag/', '/duan/', '/ooxx/', '/pic/', '/top/']
    url_tail = 'I_just_want_to_see_the_404_picture_<(=￣﹃￣=)>'

    def __init__(self, pic_dir=None):
        if '~/' in pic_dir:
            pic_dir = replace(pic_dir, '~', os.getenv('HOME'))
        self.pic_dir = pic_dir

        if not self.pic_dir:
            print('请指定存储目录')
            sys.exit()

        try:
            self.pics = os.listdir(self.pic_dir)
        except FileNotFoundError:
            os.mkdir(self.pic_dir)

    def random_404_url(self):
        return self.base_url + random.choice(self.paths) + randkey(4) + self.url_tail

    def get_404_page(self):
        url = self.random_404_url()
        html = requests.get(url).content.decode('utf-8')
        return Jiandan404Page(html)

    # page为Jiandan404Page实例
    def download_404_pic(self, page):
        headers_tankr = {
               'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.5',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'DNT': '1',
               'Host': 'tankr.net',
               'Referer': page.pic_url,
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +\
                       '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
                }
        # 这里return的是图片内容
        return requests.get(page.pic_url, headers=headers_tankr).content

    def easy_download(self):
        page = self.get_404_page()

        if not page.pic_url:
            return False

        pic_name = page.pic_url.split('/')[-1]
        if pic_name in self.pics:
            print('放弃重复抓取：' + pic_name)
            return False
        self.pics.append(pic_name)

        pic = self.download_404_pic(page)
        pic_path = os.path.join(self.pic_dir, pic_name)
        with open(pic_path, 'wb') as f:
            f.write(pic)
        return True
    
    def constantly_download(self):
        while True:
            try:
                self.easy_download()
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    argp = argparse.ArgumentParser(
                                prog='jiandan_404_picture_downloader',
                                description='煎蛋网404图片下载器',
                                epilog='出于对煎蛋网的人道主义关怀，请不要使用多线程、多进程和协程',
                                )

    argp.add_argument('-d', help='指定图片存储目录')
    argp.add_argument('-C', action='store_true', help='不停地下载')
    args = argp.parse_args()

    j = Jiandan404PicDownloader(args.d)

    if args.C:
        j.constantly_download()
    else:
        j.easy_download()
