#!/usr/bin/python3

import neovim
import os
from os import path
import sys

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
import util
from util import NvimPlugin

@neovim.plugin
class Buffers(NvimPlugin):

    def __init__(self, nvim):
        super(Buffers,self).__init__(nvim)

    @neovim.command('Bdh')
    def bdh(self):
        count = 0
        failed = 0
        for buff in self.nvim.buffers:
            info = self.nvim.funcs.getbufinfo(buff.number)
            if not info[0]['windows']:
                try:
                    self.nvim.command('bd {}'.format(buff.number))
                    count += 1
                except:
                    self.echo('bd failed for {}'.format(buff.number))
                    failed += 1
        self.echo('{} buffers deleted. {} failed'.format(count, failed))

    @neovim.command('Buffs')
    def bclh(self):
        self.nvim.current.buffer.append(['{}'.format(self.nvim.funcs.getbufinfo(buff.number)) for buff in self.nvim.buffers], 0)


