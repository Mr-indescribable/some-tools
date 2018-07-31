#!/usr/bin/python3.6
#coding: utf-8

from pyghmi.ipmi.command import Command


class Py3Ghmi():

    ''' 为 Python3 简单包装的 pyghmi
    '''

    def __init__(self, host, user, pwd, port=623, level=3):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.level = level

    def gen_ghmi_cmd(self):
        ''' 获取 pyghmi 的 Command 对象
        '''

        from pyghmi.ipmi.private.session import Session

        # 这块代码用于修复 pyghmi 的 Command 类在程序中只能使用一次的问题
        #
        # 出于某些未知原因，pyghmi 的 session 管理机制在 Python3 环境中无法
        # 正常工作，Session 类会使用一些类级成员变量来保存一些历史 session，
        # 但由于其管理机制失效，导致一些已经死亡的 session 仍然会驻留在session
        # 容器中，而 Session 类本身又存在一种类似于重复利用 session 的机制，
        # 导致其在 Session.__init__ 中无底线地等待已死亡的 session 获得服务端
        # 的响应。于是程序就会在第二次实例化 Session 类的时候卡死。
        #
        # 在我们的程序中，我们不需要重复利用旧有的 Session，每次发出 ipmi 指令
        # 时重新建立新的会话即可。所以，我们可以在实例化 Command 类的时候手动
        # 清除 Session 类中所保留的这些历史信息。如此，每次实例化 Command 类的
        # 时候 pyghmi 都会被迫建立新的 Session 以规避 Python3 环境下由 Session
        # 管理机制失效而导致的种种问题。
        Session.bmc_handlers = {}
        Session.waiting_sessions = {}
        Session.initting_sessions = {}
        Session.keepalive_sessions = {}
        Session.peeraddr_to_nodes = {}
        Session.iterwaiters = []
        Session.socketpool = {}
        Session.socketchecking = None

        return Command(
            self.host,
            self.user,
            self.pwd,
            self.port,
            privlevel=self.level,
        )

    def power_status(self):
        cmd = self.gen_ghmi_cmd()
        res = cmd.get_power()
        return res.get('powerstate')

    def power_on(self):
        cmd = self.gen_ghmi_cmd()
        return cmd.set_power('on')

    def power_off(self):
        cmd = self.gen_ghmi_cmd()
        return cmd.set_power('off')

    def power_reset(self):
        if self.power_status() == 'off':
            self.power_on()
        else:
            cmd = self.gen_ghmi_cmd()
            return cmd.set_power('reset')

    def shutdown(self):
        cmd = self.gen_ghmi_cmd()
        return cmd.set_power('shutdown')

    def set_bootdev(self, bootdev, uefiboot=False):
        cmd = self.gen_ghmi_cmd()
        return cmd.set_bootdev(bootdev, uefiboot=uefiboot)

    def get_bootdev(self):
        cmd = self.gen_ghmi_cmd()
        return cmd.get_bootdev()
