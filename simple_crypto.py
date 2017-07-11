#!/usr/bin/env python3
#coding:utf-8
import io
import sys
import base64 as b64
import argparse

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from threading import Thread, Event, Lock
from multiprocessing import Process, Queue
from multiprocessing.queues import Empty


'''
                        --------------
                        |            |
                        | CryptoType |
                        |            |
                        --------------                     ------------
                               |  -----------> queue_0 --> |          | ---------
                               |  | response               | Worker 0 |         |
                               v  |              ----------|          |         v
    --------------        ----------             | request ------------    ----------
    |            |        |        |             v               .         |        |
    | SourceFile | -----> | Master | <--- queue_request          .         | Buffer | ---> write to file
    |            |        |        |             ^               .         |        |
    --------------        ----------             | request ------------    ----------
                                  |              ----------|          |         ^
                                  | response               | Worker n |         |
                                  -----------> queue_n --> |          | ---------
                                                           ------------
'''


class SourceFile(object):
    serial = 0
    buffer_ = None

    def __init__(self, source_file, bs=None):
        self.__file = open(source_file, 'rb')
        self.bs = bs or 64

    def __file_content_to_buffer(self, type_='block', size=32):
        # 根据type_的类型，size也将会表现为不同的类型
        # 对于block，size表现为“兆字节”；对于row，size表现为“千行”
        if type_ == 'block':
            real_size = size * 1024 * 1024
            file_content = self.__file.read(real_size)

            if not file_content:
                self.__file.close()
                self.buffer_ = io.BytesIO()
                return

            self.buffer_ = io.BytesIO(file_content)

        else: # type == 'row'
            self.buffer_ = Queue()
            try:
                for i in range(size * 1000):
                    self.buffer_.put(next(self.__file))
            except StopIteration:
                self.__file.close()

    def __read_from_buffer(self, type_='block'):
        if not self.buffer_:
            self.__file_content_to_buffer(type_)

        if type_ == 'block':
            data = self.buffer_.read(self.bs)
            if data:
                return data

            self.buffer_ = None

            if self.__file.closed:
                return None
            # 若文件尚未关闭，则表示还有数据待读
            # 置空buffer递归自身一次即可返回数据
            return self.__read_from_buffer(type_)
        else: # type == 'row'
            try:
                return self.buffer_.get_nowait()
            except Empty:
                self.buffer_ = None

                if self.__file.closed:
                    return None
                # 同上，置空buffer并递归自身一次
                return self.__read_from_buffer(type_)

    def _next(self, type_):
        data = self.__read_from_buffer(type_)
        if data:
            res = {
                    'block': data,
                    'serial': self.serial,
                    }
            self.serial += 1
            return res
        return None

    def _next_block(self):
        return self._next('block')

    def _next_row(self):
        return self._next('row')


class Master(object):
    def __init__(self,
                 source_file_path,
                 crypto_type,
                 opt_type='encrypt',
                 output_file_path=None,
                 bs=None,
                 **kwargs):
        crypto_type_map = {
                'base64': CryptoBase64,
                }

        # 通信队列，worker向master请求数据用
        self.request_queue = Queue()
        # master向worker返回数据用，在start函数中生成
        self.resp_queue_map = None
        # block_size，块大小
        self.bs = bs

        # 源文件
        self.source_file = SourceFile(source_file_path, bs=bs)
        # 操作类型，指代encrypt和decrypt
        self.opt_type = opt_type

        crypto_class = crypto_type_map.get(crypto_type)
        self.crypto_type_obj = crypto_class(**kwargs)
        self.output_file_path = output_file_path or source_file_path + '.scoutput'

    def __source_file_mgr_start(self):
        if self.opt_type == 'encrypt':
            func_for_get_data = self.source_file._next_block
        else:  # self.opt_type == 'decrypt'
            func_for_get_data = self.source_file._next_row

        while True:
            data = func_for_get_data()
            if data:
                process_serial = self.request_queue.get()
                self.resp_queue_map[process_serial].put(data)
            else:
                for resp_queue in self.resp_queue_map.values():
                    resp_queue.put(None)
                break

    def start(self, workers=1):
        # 根据workers的数量生成同数量的通信队列
        self.resp_queue_map = {serial: Queue() for serial in range(workers)}
        output_handler = OutputHandler(self.output_file_path, workers)

        # 启动各种worker
        for serial in range(workers):
            worker = Worker(self.request_queue,
                            self.resp_queue_map[serial],
                            self.crypto_type_obj,
                            output_handler,
                            opt_type=self.opt_type,
                            serial=serial)
            worker.start()
        output_handler.start()

        # master开始监听request_queue
        self.__source_file_mgr_start()

        output_handler.join()


class Worker(object):
    def __init__(self,
                 request_queue,
                 resp_queue,
                 crypto_obj,
                 output_handler,
                 opt_type='encrypt',
                 serial=None):
        self.request_queue = request_queue
        self.resp_queue = resp_queue
        self.crypto_obj = crypto_obj
        self.output_handler = output_handler
        self.opt_type = opt_type
        self.serial = serial

    def request_data(self):
        self.request_queue.put(self.serial)
        return self.resp_queue.get()

    def work(self):
        while True:
            data = self.request_data()
            if data:
                if self.opt_type == 'encrypt':
                    res = self.crypto_obj.completely_encrypt(data['block'])
                else: # self.opt_type == 'decrypt'
                    res = self.crypto_obj.completely_decrypt(data['block'])

                data['block'] = res
                self.output_handler.save(data)
            else:
                self.output_handler.save('EOF')
                break

    def start(self):
        self.worker = Process(target=self.work)
        self.worker.start()

    def join(self):
        if hasattr(self, 'worker'):
            self.worker.join()
            return True


class OutputHandler(object):
    def __init__(self, output_file_path, number_of_worker):
        self.data_serial = 0
        self.evt = Event()

        self.output_file = open(output_file_path, 'wb')

        self.max_EFO_times = number_of_worker
        self.buffer_ = Queue()

    def save(self, data):
        self.buffer_.put(data)
        self.evt.set()

    def _get_all_buffered_data(self):
        return [self.buffer_.get() for i in range(self.buffer_.qsize())]

    def work(self):
        current_serial = 0
        EOF_times = 0
        # 一次循环中未处理的数据将会存在这里，和下一轮循环中的数据合并起来一起处理
        untreated = []

        while True:
            data_list = self._get_all_buffered_data()
            if not (data_list or untreated):
                continue

            # 查看并去除EOF标识
            if 'EOF' in data_list:
                current_EOF_times = data_list.count('EOF')
                EOF_times += current_EOF_times
                for i in range(current_EOF_times):
                    data_list.remove('EOF')

            # 将上一轮未处理的数据和本次数据合并，一起排序
            data_list += untreated
            untreated = []
            data_list.sort(key=lambda x: x['serial'])

            data_to_write = b''
            for d in data_list:
                # 若数据序号和当前序号不同，则是出现断片，break之后读取后续数据
                if data_list[0]['serial'] == current_serial:
                    data_to_write += data_list.pop(0)['block']
                    current_serial += 1
                else:
                    break

            self.output_file.write(data_to_write)

            # 保存没有处理完的数据
            if data_list:
                untreated = data_list

            # 所有worker都已停止，所有数据都已处理完毕，退出
            if EOF_times == self.max_EFO_times and not untreated:
                self.output_file.close()
                break

            self.evt.wait(timeout=0.1)

    def start(self):
        self.worker = Thread(target=self.work)
        self.worker.start()

    def join(self):
        if hasattr(self, 'worker'):
            self.worker.join()
            return True


class CryptoClassMixin(object):
    def __init__(self, *args, **kwargs):
        self.a = 0

    def completely_encrypt(self, data):
        encrypted = self.encrypt(data)
        return self.after_encrypt(encrypted)

    def completely_decrypt(self, data):
        real_data = self.before_decrypt(data)
        return self.decrypt(real_data)

    def after_encrypt(self, data):
        return b64.standard_b64encode(data) + b'\n'

    def before_decrypt(self, data):
        return b64.standard_b64decode(data.rstrip(b'\n'))

    def encrypt(self, data):
        return data

    def decrypt(self, data):
        return data


class CryptoBase64(CryptoClassMixin):
    def encrypt(self, data):
        return b64.b64encode(data)

    def decrypt(self, data):
        return b64.b64decode(data)


if __name__ == '__main__':
    m = Master('a', 'base64', opt_type='encrypt', output_file_path='encoded', bs=1024)
    # m = Master('encoded', 'base64', opt_type='decrypt', output_file_path='decoded')
    m.start(workers=4)
