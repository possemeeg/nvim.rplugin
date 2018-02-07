#!/usr/bin/python3

import neovim
import subprocess
import re
import sys
import os
from os import path

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
from util import NvimPlugin

MVN_ERROR_REGEX = re.compile(r'^\[(ERROR|INFO|WARNING)\]\s+([^:\[]+):*\[([0-9]+),([0-9]+)\]\s*(.*)$')
MVN_END_OF_OUTPUT_REGEX = re.compile(r'^\[INFO\]\s+BUILD (SUCCESS|FAILURE)\s*$')
MVN_BUILD_BUFFER_NAME = "mavenbuildoutput.txt"

@neovim.plugin
class MavenPlugin(NvimPlugin):
    def __init__(self, nvim):
        super(MavenPlugin,self).__init__(nvim)

    @neovim.command('Mbuild', nargs='*')
    def mbuild(self, args):
        def _jmvn(outbuffer, builddir):
            mvn_out = []
            self.echo('building')
            result = self.build(outbuffer, builddir, lambda sev, file, line, col, msg:
                    mvn_out.append({'type': sev[0:1], 'lnum': line, 'filename':file, 'col': col, 'valid': 1, 'vcol': 0,
                        'nr': -1, 'type': '', 'pattern': '', 'text': '{}: {}'.format(sev, msg)}))
            self.nvim.funcs.setqflist(mvn_out)
            if result != 0:
                self.nvim.command('copen')
                self.echo('build ready')
            else:
                self.nvim.command('cclose')
                self.echo('build success')
        currentdir = self.nvim.funcs.getcwd()
        outbuffer = self._get_or_create_build_buffer(currentdir)
        self.nvim.async_call(_jmvn, outbuffer, currentdir)

    @neovim.command('Mkillout')
    def mkillout(self):
        count = 0
        for outbuffer in self.findbuffers(MVN_BUILD_BUFFER_NAME):
            self.nvim.command('bw! {}'.format(outbuffer.number))
            count += 1
        self.echo('{} buffers removed'.format(count))

    @neovim.autocmd('VimLeavePre', sync=True)
    def automkillout(self):
        self.mkillout()

    def build(self, outbuffer, builddir, callback):
        completed_proc = subprocess.run(['mvn', '--batch-mode', 'clean', 'install'],stderr=subprocess.STDOUT,stdout=subprocess.PIPE,encoding="utf-8",cwd=builddir)
        extracting = True
        for line in completed_proc.stdout.splitlines():
            if outbuffer:
                outbuffer.append([line])
            if extracting:
                self._maven_extract(line, callback) 
            if MVN_END_OF_OUTPUT_REGEX.match(line):
                extracting = False
        return completed_proc.returncode

    def _maven_extract(self, line, callback):
        match = MVN_ERROR_REGEX.match(line)
        if match:
            callback(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))

    def _get_or_create_build_buffer(self, cwd):
        fullname = path.realpath(path.join(cwd,MVN_BUILD_BUFFER_NAME))
        outbuffer = self.findbuffer(fullname)
        if not outbuffer:
            self.nvim.command('badd {}'.format(fullname))
            outbuffer = self.findbuffer(fullname)
        return outbuffer
