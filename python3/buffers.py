#!/usr/bin/python3

import neovim
import os
from os import path
import sys
import operator

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
import util
from util import NvimPlugin

@neovim.plugin
class Buffers(NvimPlugin):

    def __init__(self, nvim):
        super(Buffers,self).__init__(nvim)
        self.items = []

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
                    pass
        self.echo(f'{count} buffers deleted.')

    @neovim.command('Bufs', nargs='*')
    def bclh(self, nargs):
        out = []
        count = int(nargs[0]) if nargs and len(nargs) > 0 else 10
        for buf in reversed(self.items):
            out.append({'type': '', 'filename': buf[0], 'col': 0, 'valid': 1, 'vcol': 0,
                'nr': -1, 'type': '', 'pattern': '', 'text': '{}'.format(self.nvim.funcs.strftime('%T', buf[1]))})
            count = count - 1;
            if count <= 0:
                break;

        self.nvim.funcs.setqflist(out)
        self.nvim.command('copen')

    @neovim.autocmd('BufEnter', pattern='*', eval='expand("<afile>")', sync=True)
    def on_bufenter(self, buffername):
        bufinfo = self.nvim.funcs.getbufinfo(buffername) if buffername and not buffername.startswith('NERD_tree') else None
        if bufinfo and len(bufinfo) > 0 and  bufinfo[0]['listed']:
            buffername = bufinfo[0]['name']
            while (True):
                delindexes = [i for (i,j) in enumerate(self.items) if j[0] == buffername]
                if not delindexes:
                    break
                del(self.items[delindexes[0]])

            self.items.append([buffername, self.nvim.funcs.localtime()])


