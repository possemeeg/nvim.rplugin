#!/usr/bin/python3

import os
from os import path
import re

class RootSeeker(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.parent_dirname = path.dirname(dirname)

    def backseek(self, suffixs, stopatfirstrootmatch=False):
        for suffix in suffixs:
            foundpath=self._backseek(suffix, stopatfirstrootmatch)
            if foundpath:
                return foundpath

    def _backseek(self, suffix, stopatfirstrootmatch):
        if self._ismatch(suffix):
            if stopatfirstrootmatch or self._isroot():
                return self.dirname
            parent_tester = RootSeeker(self.parent_dirname)
            return parent_tester.dirname if parent_tester._ismatch(suffix) else self.dirname
        return RootSeeker(self.parent_dirname)._backseek(suffix, stopatfirstrootmatch) if not self._isroot() else None

    def _ismatch(self, suffix):
        return path.exists(path.join(self.dirname,suffix))
    
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

    def getorcreatebuffer(self, name):
        foundbuffer = self.findbuffer(name)
        if foundbuffer:
            return foundbuffer
        self.nvim.command('badd {}'.format(name))
        dirname = path.dirname(name)
        if not path.exists(dirname):
            os.makedirs(dirname)
        return self.findbuffer(name)

