#!/usr/bin/python3

import neovim
import os
from os import path
import sys
import operator
import glob

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
import util
from util import NvimPlugin

@neovim.plugin
class Find(NvimPlugin):

    def __init__(self, nvim):
        super(Find,self).__init__(nvim)

    @neovim.command('Ff', nargs='*')
    def find_files(self, nargs):
        out = []
        pattern = nargs[0] if nargs and len(nargs) > 0 else '*'

        os.chdir(self.nvim.funcs.getcwd())

        for filename in sorted(glob.glob(pattern, recursive=True)):
            out.append({'type': '', 'filename': filename, 'col': 0, 'valid': 1, 'vcol': 0,
                'nr': -1, 'type': '', 'pattern': '', 'text': '{}'.format(os.path.basename(filename))})

 
        self.nvim.funcs.setqflist(out)
        self.nvim.command('copen')




