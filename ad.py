#!/usr/bin/python3.6
#coding: utf-8

import json

from ldap3 import Server, Connection, NTLM, ALL_ATTRIBUTES

from objectified_dict import ObjectifiedDict


class ADClient():

    '''
        简单封装的 MS-AD 客户端

        提供认证和获取域账号信息功能
    '''

    def __init__(self, user, pwd, domain, host,
                       port=None, domain_abb=None, use_ssl=False):
        ''' 构造函数

        :参数 user: 不带域前缀的用户名，str
        :参数 pwd: 密码
        :参数 domain: AD 域全名
        :参数 host: 域控服务器地址
        :参数 port: 域控服务器端口
        :参数 domain_abb: 域简称，默认为 domain 参数的最小子域
        :参数 use_ssl: 是否使用 ssl (ldaps)
        '''

        self.user = user
        self.pwd = pwd
        self.domain = domain
        self.host = host
        self.port = port or (636 if use_ssl else 389)
        self.domain_abb = domain_abb or domain.split('.')[0].upper()
        self.use_ssl = use_ssl

        # 完整的域账号，域前缀加用户名
        self.ad_user = '%s\\%s' % (self.domain_abb, self.user)

        # 将 domain 换算成 LADP 的 DC
        dcs = ['DC=%s' % dc for dc in domain.split('.')]
        self.dc = ', '.join(dcs)

        self.server = Server(
                          self.host,
                          self.port,
                          use_ssl=self.use_ssl,
                      )
        self.conn = Connection(
                        self.server,
                        user=self.ad_user,
                        password=self.pwd,
                        authentication=NTLM,
                    )

    def auth(self):
        return self.conn.bind()

    def get_user(self, name=None):
        ''' 从域控服务器中查询用户的详细信息

        :参数 name: 域用户名，str，默认为 self.user
        :return: 找到的用户列表，list，[ObjectifiedDict]
        '''

        name = name or self.user

        # AD 认证的时候，实际读取的用户名字段是 sAMAccountName
        search_filter = '''
        (&
            (objectclass=user)
            (sAMAccountName=%s)
        )
        ''' % name

        found = self.conn.search(
                    self.dc,
                    search_filter,
                    attributes=ALL_ATTRIBUTES,
                )
        if not found:
            return []
        else:
            return [
                ObjectifiedDict(
                    **json.loads(entry.entry_to_json())
                )
                for entry in self.conn.entries
            ]

    def __del__(self):
        self.conn.unbind()
