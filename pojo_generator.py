#!/usr/bin/python3.6
#coding: utf-8

import os
import importlib


FILE_TEMP = (
    'package %(pkg_name)s;\n\n\n'
    '%(pojo_body)s'
)

CLASS_TEMP = (
    'public class %(name)s {\n\n'
    '%(attrs)s\n\n'
    '%(getters)s\n\n'
    '%(setters)s\n\n'
    '}'
)

ATTR_TEMP = '\tprivate %(type)s %(name)s;'

GETTER_TEMP = (
    '\tpublic %(type)s %(func_name)s() {\n'
    '\t\treturn this.%(attr_name)s;\n'
    '\t}'
)

SETTER_TEMP = (
    '\tpublic void %(func_name)s(%(type)s %(attr_name)s) {\n'
    '\t\tthis.%(attr_name)s = %(attr_name)s;\n'
    '\t}'
)


class PojoGenerator():

    '''Java POJO 生成器

    一个用于生成 Java POJO 代码的小工具
    可以读取 Python 类或模块并生成对应的 POJO

    用法用例：

        1. 从类中生成代码字符串：

            # POJO 类即 Python 类，类名对应 POJO 类名
            # 其中每项属性对应 POJO 类中的各个属性
            # 每个属性的值为 Java 类型, str 格式
            Class Pojo:

                attr0 = 'int'
                attr1 = 'String'
                attr2 = 'List<String>'

            generator = PojoGenerator()
            generator.gen_str_from_class(Pojo)

        2. 从 Python 模块中生成代码字符串：
            
            类的声明方式与用法 1 相同，将多个 POJO 类放在一个模块里
            并将模块名作为参数传给 gen_str_from_module

            generator = PojoGenerator()
            pojos = generator.gen_str_from_module('pojo_pkg.pojo_module')

        3. 生成代码输出到对应目录:

            可以选择从 Python 类或模块中生成代码，并写入到对应目录下的文件中
            类的声明方式与上面 2 种用法相同，需要配置额外属性 __pkg__，
            __pkg__ 为 Java 包名，str 格式

            完成类或模块的编写之后，使用 gen_file_from_* 函数来生成 POJO 文件
    '''

    def __init__(self, pkg_root='./'):
        ''' 构造函数

        :param pkg_root: Java 顶级包（如com, org）所在目录，str
        '''

        if not os.path.isdir(pkg_root):
            raise FileNotFoundError('pkg_root dosn\'t exist')

        self.root = pkg_root

    def render_class(self, name, attrs, getters, setters):
        return CLASS_TEMP % {
            'name': name,
            'attrs': '\n'.join(attrs),
            'getters': '\n\n'.join(getters),
            'setters': '\n\n'.join(setters),
        }

    def render_attr(self, attr_type, attr_name):
        return ATTR_TEMP % {
            'type': attr_type,
            'name': attr_name,
        }

    def render_getter(self, rtype, func_name, attr_name):
        return GETTER_TEMP % {
            'type': rtype,
            'func_name': func_name,
            'attr_name': attr_name,
        }

    def render_setter(self, arg_type, func_name, attr_name):
        return SETTER_TEMP % {
            'func_name': func_name,
            'type': arg_type,
            'attr_name': attr_name,
        }

    @classmethod
    def filter(cls, obj):
        return {
            k: v for k, v in obj.__dict__.items()
            if not (k.startswith('__') and k.endswith('__'))
        }

    def attrnm_2_getternm(self, attr_name):
        func_name = attr_name.upper()[0] + attr_name[1:]
        return 'get' + func_name

    def attrnm_2_setternm(self, attr_name):
        func_name = attr_name.upper()[0] + attr_name[1:]
        return 'set' + func_name

    def gen_str_from_class(self, cls, with_pkg=False):
        attrs = []
        getters = []
        setters = []

        filtered_obj = self.filter(cls)
        for attr_name, attr_type in filtered_obj.items():
            attrs.append(
                self.render_attr(attr_type, attr_name)
            )

            getter_name = self.attrnm_2_getternm(attr_name)
            getters.append(
                self.render_getter(attr_type, getter_name, attr_name)
            )

            setter_name = self.attrnm_2_setternm(attr_name)
            setters.append(
                self.render_setter(attr_type, setter_name, attr_name)
            )

        class_name = cls.__name__
        pojo = self.render_class(
                   class_name,
                   attrs,
                   getters,
                   setters,
               )

        if with_pkg:
            return FILE_TEMP % {
                       'pkg_name': cls.__pkg__,
                       'pojo_body': pojo,
                   }
        else:
            return pojo

    def gen_str_from_module(self, module_path):
        module = importlib.import_module(module_path)
        pojo_names = self.filter(module)

        return [
            self.gen_str_from_class(getattr(module, pojo_name))
            for pojo_name in pojo_names
        ]

    def gen_file_from_class(self, cls):
        code = self.gen_str_from_class(cls, with_pkg=True)

        try:
            pkg = getattr(cls, '__pkg__')
        except AttributeError:
            raise AttributeError(
                'You need to define attribute __pkg__ for POJO class '
                'when you are using function gen_file_from_*'
            )

        relative_path = pkg.replace('.', '/')
        self._write(code, cls.__name__, relative_path)

    def gen_file_from_module(self, module_path):
        module = importlib.import_module(module_path)
        pojo_names = self.filter(module)

        for pojo_name in pojo_names:
            cls = getattr(module, pojo_name)
            self.gen_file_from_class(cls)

    def _write(self, code, cls_name, relative_path=''):
        real_dir = os.path.join(self.root, relative_path)
        if not os.path.isdir(real_dir):
            os.makedirs(real_dir)

        filename = cls_name + '.java'
        file_path = os.path.join(real_dir, filename)
        with open(file_path, 'w') as f:
            f.write(code)

        print('Generated\t%s' % file_path)


if __name__ == '__main__':
    def test_gen_file():
        generator = PojoGenerator(pkg_root='./pojos')
        generator.gen_file_from_module('pojos')

    test_gen_file()
