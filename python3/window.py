#!/usr/bin/python3

import neovim
import os
from os import path
import sys

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
import util
from util import NvimPlugin

@neovim.plugin
class Window(NvimPlugin):

    def __init__(self, nvim):
        super(Window,self).__init__(nvim)

    @neovim.command('Wlim', nargs='*')
    def wlim(self, args):
        self.nvim.command('highlight OverLength ctermbg=red ctermfg=white guibg=#592929')
        self.nvim.command('match OverLength /\%{}v.\+/'.format(args[0]))

