#!/usr/bin/python3

import neovim
import subprocess
import re
import sys
import os
from os import path

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
from util import NvimPlugin

OUTPUT_BUFFER_NAME = "background-command-output"

@neovim.plugin
class BackgroundCommandPlugin(NvimPlugin):
    def __init__(self, nvim):
        super(BackgroundCommandPlugin,self).__init__(nvim)

    @neovim.command('Bcmd', nargs='*')
    def bcmd(self, args):
        def _bcmd(command, outbuffer, builddir):
            cmd_out = []
            self.echo('Running command {} in directory {} - output to {}'.format(command, builddir, OUTPUT_BUFFER_NAME))
            del(outbuffer[0:len(outbuffer)])
            completed_proc = subprocess.run(args,stderr=subprocess.STDOUT,stdout=subprocess.PIPE,encoding="utf-8",cwd=builddir)
            for line in completed_proc.stdout.splitlines():
                outbuffer.append([line])
        currentdir = self.nvim.funcs.getcwd()
        outbuffer = self._get_or_create_build_buffer(currentdir)
        self.nvim.async_call(_bcmd, args, outbuffer, currentdir)

    @neovim.command('Bsout')
    def bout(self):
        lines = []
        for outbuffer in self.findbuffers(OUTPUT_BUFFER_NAME):
            lines.append({'type': '', 'lnum': 0, 'filename':outbuffer.name, 'col': 0, 'valid': 1, 'vcol': 0,
                        'nr': -1, 'type': '', 'pattern': '', 'text': 'Command in {}'.format(path.dirname(outbuffer.name))})
        self.nvim.funcs.setqflist(lines)
        self.nvim.command('copen')

    @neovim.command('Bkout')
    def bkout(self):
        count = 0
        for outbuffer in self.findbuffers(OUTPUT_BUFFER_NAME):
            self.nvim.command('bw! {}'.format(outbuffer.number))
            count += 1
        self.echo('{} buffers removed'.format(count))

    @neovim.autocmd('VimLeavePre', sync=True)
    def autobkout(self):
        self.mkillout()

    def _get_or_create_build_buffer(self, cwd):
        fullname = path.realpath(path.join(cwd,OUTPUT_BUFFER_NAME))
        outbuffer = self.findbuffer(fullname)
        if not outbuffer:
            self.nvim.command('badd {}'.format(fullname))
            outbuffer = self.findbuffer(fullname)
        return outbuffer

