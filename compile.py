#!/usr/bin/python3.6
#coding: utf-8

import os
from shutil import copyfile
from distutils.core import setup

from Cython.Build import cythonize


class PyCompiler():

    ''' Python code compiler

    This compiler can help you to compile Python code files to .so libraries.

    Actually, it will exclude all __init__.py files and compile others,
    and copy __init__.py files into the compiled project after compilation.

    Usage:
        ./compile.py your_python_project
    '''

    @classmethod
    def copy_init_dot_py(cls, src, dest='./build/lib.linux-x86_64-3.6'):
        ''' copy __init__.py files

        This function will recursively copy all __init__.py files in the source
        directory into the destination directory in the same relative path.

        :param src: The source directory where __init__.py could exist.
                    In other words, the root directory of your Python project.
        :param dest: The destination directory where __init__.py should go.
                     In other words, it's the directory that contains the
                     root directory of the compiled project.
        '''

        files = os.listdir(src)

        if '__init__.py' in files:
            copyfile(
                os.path.join(src, '__init__.py'),
                os.path.join(dest, src, '__init__.py'),
            )

        for fl in files:
            fl_path = os.path.join(src, fl)
            if os.path.isdir(fl_path):
                cls.copy_init_dot_py(fl_path, dest)

    @classmethod
    def compile(cls, modules, exclude=None, **kwargs):
        ''' compiles Python code file by invoking distutils.core.setup

        All these arguments will be passed into function distutils.core.setup
        '''

        setup(
            script_args=['build'],
            ext_modules=cythonize(modules, exclude=exclude, **kwargs),
        )

    @classmethod
    def compile_dir(cls, path):
        ''' compile directory
        
        Recursively compile all Python code files in a directory
        except __init__.py.
        '''

        files = os.listdir(path)

        cls.compile(
            modules=[os.path.join(path, '*.py')],
            exclude=[os.path.join(path, '__init__.py')]
        )
        for fl in files:
            fl_path = os.path.join(path, fl)
            if os.path.isdir(fl_path):
                cls.compile_dir(fl_path)

    @classmethod
    def compile_project(cls, path):
        ''' compile your Python project
        '''

        cls.compile_dir(path)
        cls.copy_init_dot_py(path)


if __name__ == '__main__':
    import sys
    PyCompiler.compile_project(sys.argv[1])
