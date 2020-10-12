#!/usr/bin/python3
import neovim
import os
import sys
import operator
import glob
import re
import subprocess

sys.path.append(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))))
import util
from util import NvimPlugin

AG_RESULT = re.compile(r'^(?P<filename>[^:]+):(?P<lnum>[0-9]+):(?P<col>[0-9]+):(?P<text>.*)$')

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

    @neovim.command('Ag', nargs='+')
    def custom_grep(self, args):
        out = []
        for line in self._custom_grep(args, self.nvim.funcs.getcwd()):
            out.append(line)

        self.nvim.funcs.setqflist(out)
        self.nvim.command('copen')

    def _custom_grep(self, args, base_dir):
        out = []
        pattern = args[0]
        if len(args) > 1:
            givin_dir = os.path.expanduser(args[1])
            base_dir = givin_dir if givin_dir.startswith('/') else os.path.normpath(os.path.join(base_dir, givin_dir))

        yield {'type': '', 'filename': '', 'lnum': 0, 'col': 0, 'valid': 1, 'vcol': 0,
            'nr': -1, 'type': '', 'pattern': '', 'text': f'Searching for {pattern} in path: {base_dir}' }

        call = ['ag','--case-sensitive','--nogroup','--nocolor','--column']
        if pattern.startswith('\<') and pattern.endswith('\>'):
            pattern = pattern[2:][:-2]
            call += ['-w']
        call += [pattern, base_dir]

        try:
            outp = subprocess.Popen(call, stdout=subprocess.PIPE)
            while 42:
                line = outp.stdout.readline()
                if not line:
                    break
                match = AG_RESULT.match(line.decode())
                if match:
                    gd = match.groupdict();
                    yield {'type': '', 'filename': gd['filename'], 'lnum': gd['lnum'], 'col': gd['col'], 'valid': 1, 'vcol': 0,
                        'nr': -1, 'type': '', 'pattern': '', 'text': gd['text']}

        except subprocess.CalledProcessError as err:
            print(err.output)


if __name__ == '__main__':
    for line in Find(None)._custom_grep(['class', '.'], os.getcwd()):
        print(line)



