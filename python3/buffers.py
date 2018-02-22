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
    def bclh(self):
        self.nvim.command(Non)

        for buff in self.nvim.buffers:
            if buff.hidden:
                self.nvim.command('bd {}'.format(buff.number))
