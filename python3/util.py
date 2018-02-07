#!/usr/bin/python3

import os
from os import path
import re

class RootSeeker(object):
    def __init__(self, dirname, suffix):
        self.dirname = dirname
        self.suffix = suffix
        self.test_path = path.join(dirname,suffix)
        self.parent_dirname = path.dirname(dirname)

    def backseek(self, first=False):
        if self._ismatch():
            if first or self._isroot():
                return self.dirname
            parent_tester = RootSeeker(self.parent_dirname, self.suffix)
            return parent_tester.dirname if parent_tester._ismatch() else self.dirname
        return RootSeeker(self.parent_dirname, self.suffix).backseek(first) if not self._isroot() else None

    def _ismatch(self):
        test = path.exists(self.test_path)
        return test
    
    def _isroot(self):
        return not self.dirname or self.parent_dirname == self.dirname
    
class LeafDirectoryFinder(object):
    def __init__(self, rootdirname, filere):
        self.rootdirname = path.realpath(rootdirname)
        self.filere = filere

    def alldirs(self):
        alldirs = []
        for root, dirs, files in os.walk(self.rootdirname): 
            brk = False
            for f in files:
                if self.filere.match(f):
                    alldirs.append(root)
                    break

        return alldirs

class NvimPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim

    def echo(self, message):
        self.nvim.command('echo "{}"'.format(self.nvim.funcs.escape(message, '"')))

    def findbuffer(self, name):
        for buff in self.nvim.buffers:
            if buff.name == name:
                return buff

    def findbuffers(self, name):
        for buff in self.nvim.buffers:
            if name in buff.name:
                yield buff

