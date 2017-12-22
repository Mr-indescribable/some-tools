#!/usr/bin/python3
#coding: utf-8

import sys
import copy
import json


''' 递归对象化多层字典嵌套形式的配置，将所有嵌套的字典转化成Config对象

使用：
    before:
        config['a']['b']['c']

    after:
        config.a.b.c


存储结构：
    before:
        {
            "x": "X",
            "a": {
                "y": "Y",
                "b": {
                    "c": "The Value!"
                }
            }
        }

    after:
        {
            "x": "X",
            "a": new_config_instance_0
        }

        new_config_instance_0: {
                                   "y": "Y",
                                   "b": new_config_instance_1
                               }

        new_config_instance_1: {
                                   "c": "The Value!"
                               }
'''


class Config():

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            conf = object.__getattribute__(self, '_conf')
            return conf.get(name)

    def __str__(self):
        return json.dumps(self._raw_conf, indent=4)

    def __init__(self, sh_args=None, dict_style_conf=None):
        if sh_args:
            config_path = sh_args.c
            try:
                with open(config_path, 'r') as cf:
                    conf = cf.read()
            except FileNotFoundError:
                print('Cannot open %s: No such file or directory' % config_path)
                sys.exit(1)
            except PermissionError:
                print('Cannot open %s: Permission denied' % config_path)
                sys.exit(1)

            try:
                conf = json.loads(conf)
            except json.decoder.JSONDecodeError:
                print('Json formation error in config file, please recheck')
                sys.exit(1)
            conf['__sh_args__'] = dict(sh_args._get_kwargs())
            self._conf = conf
            self._raw_conf = copy.deepcopy(conf)
        elif dict_conf:
            self._conf = dict_style_conf
            self._raw_conf = copy.deepcopy(dict_style_conf)

        self.__magnificently_objectify()

    def __magnificently_objectify(self):
        dict_conv_list = []
        list_conv_list = []
        for k, v in self._conf.items():
            if isinstance(v, dict):
                dict_conv_list.append(k)
            if isinstance(v, list):
                list_conv_list.append(k)
        for k in dict_conv_list:
            self._conf[k] = Config(dict_conf=self._conf[k])
        for k in list_conv_list:
            self._conf[k] = [
                Config(dict_conf=dc) for dc in self._conf[k]
                if isinstance(dc, dict)
            ]
