#!/usr/bin/python3.6
#coding: utf-8

import re
import time

import requests


HOME = 'https://www.v2ex.com/?tab=all'


class V2EXBlocker():

    '''
        BLOCK ALL THESE M*****F*****s !!!
    '''

    def __init__(self, cookies={}):
        self._cookies = cookies

    def __get(self, url):
        return requests.get(url=url, cookies=self._cookies)


    def block(self, uid):
        url = 'https://www.v2ex.com/block/%d?t=1445741587' % uid
        self.__get(url)
        print('blocked UID=%d' % uid)

    def block_all(self):
        uid = 0
        while True:
            try:
                self.block(uid)
            except:
                pass
            uid += 1
            time.sleep(2)

    @property
    def home_page(self):
        return self.__get(HOME).content.decode('utf-8')


if __name__ == '__main__':
    cookies = {}

    vb = V2EXBlocker(cookies)
    vb.block_all()
