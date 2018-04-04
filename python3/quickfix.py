#!/usr/bin/python3

import neovim
import re
import sys
import os
from os import path

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
from util import NvimPlugin

MVN_ERROR_REGEX = re.compile(r'^\[(?P<type>ERROR|INFO|WARNING)\]\s+(?P<file>[^:\[]+):*\[(?P<line>[0-9]+),(?P<col>[0-9]+)\]\s*(?P<msg>.*)$')
CHECKSTYLE_ERROR_REGEX_8 = re.compile(r'^\[(?P<type>ERROR|INFO|WARNING)\]\s+(?P<file>[^:\[]+):*(?P<line>[0-9]+):(?P<col>[0-9]+){0,1}[:\s]*(?P<msg>.*)$')
CHECKSTYLE_ERROR_REGEX_7 = re.compile(r'^(?P<file>[^:\[]+):*(?P<line>[0-9]+):(?P<col>[0-9]+){0,1}[:\s]*(?P<msg>.*)$')
ALL = [MVN_ERROR_REGEX, CHECKSTYLE_ERROR_REGEX_8, CHECKSTYLE_ERROR_REGEX_7]

@neovim.plugin
class QuickFix(NvimPlugin):
    def __init__(self, nvim):
        super(QuickFix,self).__init__(nvim)

    @neovim.command('Pr', sync=True)
    def pr(self):
        self._preg(QuickFix._all_extract)

    def _preg(self, fn):
        mvn_out = []
        lines = self.nvim.funcs.getreg('+')
        for line in lines.splitlines():
            fn(line, lambda sev, file, line, col, msg:
                    mvn_out.append({'type': sev[0:1], 'lnum': line, 'filename':file, 'col': col, 'valid': 1, 'vcol': 0,
                        'nr': -1, 'type': '', 'pattern': '', 'text': '{}: {}'.format(sev, msg)}))
        self.nvim.funcs.setqflist(mvn_out)
        self.nvim.command('copen')

    @staticmethod
    def _all_extract(line, callback):
        for regex in ALL:
            match = regex.match(line)
            if match:
                matchdict = match.groupdict();
                callback(matchdict['type'] if 'type' in matchdict else 'ERROR', matchdict['file'], matchdict['line'], matchdict['col'], matchdict['msg'])
    
if __name__ == '__main__':
    mvnline = "[ERROR] /home/peter/pmg/dev/javasimple/src/main/java/com/possemeeg/javatest/App.java:[25,15] ';' expected"

    QuickFix._maven_extract(mvnline, lambda sec, file, line, col, msg:
            print("mvn: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))

    cksline1 = "[ERROR] /home/peter/pmg/dev/javasimple/src/main/java/com/possemeeg/javatest/App.java:25: ';' expected"
    QuickFix._checkstyle_extract(cksline1, lambda sec, file, line, col, msg:
            print("cks1: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))

    cksline2 = "[ERROR] /home/peter/pmg/dev/javasimple/src/main/java/com/possemeeg/javatest/App.java:25:15: ';' expected"
    QuickFix._checkstyle_extract(cksline2, lambda sec, file, line, col, msg:
            print("cks2: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))

