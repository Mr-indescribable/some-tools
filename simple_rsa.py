#!/usr/bin/env python3
#coding:utf-8
import sys
import argparse

from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA512

class SimpleRsa(object):
    def __init__(self, public_key=None, private_key=None):
        if not (public_key or private_key):
            public_key, private_key = self.rsa_key_gen()
        self.public_key = public_key
        self.private_key = private_key

    @classmethod
    def rsa_key_gen(cls, length=2048):
        seed = RSA.generate(length)
        private = seed.exportKey('PEM').decode('utf-8')
        public = seed.publickey().exportKey('PEM').decode('utf-8')
        return public, private

    def rsa_encode(self, public_key, data):
        the_key = RSA.importKey(public_key.encode('utf-8'))
        clp = PKCS1_OAEP.new(the_key, hashAlgo=SHA512)
        return clp.encrypt(data)

    def rsa_decode(self, private_key, data):
        the_key = RSA.importKey(private_key.encode('utf-8'))
        clp = PKCS1_OAEP.new(the_key, hashAlgo=SHA512)
        return clp.decrypt(data)

    def encode_data(self, data, public_key=None):
        if not public_key:
            public_key = self.public_key

        blocks = [data[i: i+5] for i in range(0, len(data), 5)]
        res = str()
        for block in blocks:
            encoded = self.rsa_encode(public_key, block.encode())
            b64data = b64encode(encoded).decode()
            res += b64data
        return res

    def decode_data(self, data, private_key=None):
        if not private_key:
            private_key = self.private_key

        blocks = [data[i: i+344] for i in range(0, len(data), 344)]
        res = str()
        for block in blocks:
            b64decoded_data = b64decode(block.rstrip('\n'))
            decoded = self.rsa_decode(private_key, b64decoded_data)
            res += decoded.decode('utf-8')
        return res


def write_down(file_name, data):
    with open(file_name, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    argp = argparse.ArgumentParser(
                                prog='simple_rsa',
                                description='一个简单的rsa加密工具',
                                epilog='注意：若没有指定公钥和私钥，将会自动生成一对密钥用于加密。'
                                )

    argp.add_argument('-data', help='直接以参数形式提供待加密数据，并优先使用此选项')
    argp.add_argument('--print', action='store_true', help='仅print，不写入文件')
    argp.add_argument('-f', help='指定输入文件')
    argp.add_argument('-of', help='指定输出文件')
    argp.add_argument('-e', action='store_true', help='执行加密操作')
    argp.add_argument('-d', action='store_true', help='执行解密操作')
    argp.add_argument('-pub', help='指定公钥文件')
    argp.add_argument('-pri', help='指定私钥文件')
    argp.add_argument('--key-gen', action='store_true', help='生成一对密钥并退出程序')
    argp.add_argument('--key-len', default=2048, type=int, help='指定生成密钥的长度')
    argp.add_argument('-opub', default='simple_rsa.pub', help='指定输出的公钥文件名')
    argp.add_argument('-opri', default='simple_rsa.pri', help='指定输出的私钥文件名')
    args = argp.parse_args()

    ## 执行--key-gen并退出
    if args.key_gen:
        pub, pri = SimpleRsa.rsa_key_gen(length=args.key_len)
        if args.print:
            print(pub)
            print(pri)
        else:
            write_down(args.opub, pub)
            write_down(args.opri, pri)
        sys.exit()

    ## 一些参数验证
    if args.e and args.d:
        print('有错误的参数，加密和解密选项不应该同时出现')
        sys.exit()
    elif not(args.e or args.d):
        print('请指定操作类型')
        sys.exit()
    if args.d and not args.pri:
        print('未指定解密密钥')
        sys.exit()

    ## 获取密钥并初始化
    public_key = None
    private_key = None
    # 加密操作读取公钥
    if args.pub and args.e:
        with open(args.pub, 'r') as f:
            public_key = f.read()
        sr = SimpleRsa(public_key=public_key)
    else:
        sr = SimpleRsa()
    # 如果是没有给出密钥的加密操作，则输出生成的密钥
    if args.e and not args.pub:
        if args.print:
            print('\n公钥：')
            print(sr.public_key)
            print('\n私钥：')
            print(sr.private_key)
        else:
            if sr.public_key:
                write_down(args.opub, sr.public_key)
            if sr.private_key:
                write_down(args.opri, sr.private_key)
    # 解密操作读取私钥
    if args.pri and args.d:
        with open(args.pri, 'r') as f:
            private_key = f.read()
        sr = SimpleRsa(private_key=private_key)

    ## 获取数据
    data = None
    if not (args.data or args.f):
        print('没有需要加密的内容')
    if args.data:
        data = args.data
    if not data:
        with open(args.f, 'r') as f:
            data = f.read()
    if not data:
        print('没有需要加密的内容')
        sys.exit()

    ## 执行加密操作
    if args.e:
        encoded_data = sr.encode_data(data)
        if args.print:
            print('\n加密后的数据：')
            print(encoded_data)
        else:
            if args.f and not args.of:
                encoded_file_name = args.f + '.srb64'
            if args.data and not args.of:
                encoded_file_name = 'simple_rsa_output.rsb64'
            write_down(encoded_file_name, encoded_data)

    ## 执行解密操作
    if args.d:
        decoded_data = sr.decode_data(data)
        if args.print:
            print('\n解密后的数据：')
            print(decoded_data)
        else:
            if args.f and not args.of:
                if args.f.endswith('.rsb64'):
                    decoded_file_name = args.f.rstrip('.srb64')
                else:
                    decoded_file_name = args.f + '.decoded'
            if args.data and not args.of:
                decoded_file_name = 'simple_rsa_output.rsb64'
            write_down(decoded_file_name, decoded_data)
