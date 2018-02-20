#!/usr/bin/python3

import neovim
import re
import sys
import os
from os import path

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
from util import NvimPlugin

MVN_ERROR_REGEX = re.compile(r'^\[(ERROR|INFO|WARNING)\]\s+([^:\[]+):*\[([0-9]+),([0-9]+)\]\s*(.*)$')
CHECKSTYLE_ERROR_REGEX = re.compile(r'^\[(ERROR|INFO|WARNING)\]\s+([^:\[]+):*([0-9]+):([0-9]+){0,1}[:\s]*(.*)$')

@neovim.plugin
class QuickFix(NvimPlugin):
    def __init__(self, nvim):
        super(QuickFix,self).__init__(nvim)

    @neovim.command('Prmvn', sync=True)
    def prmvn(self):
        self._preg(QuickFix._maven_extract)

    @neovim.command('Prcks', sync=True)
    def prcks(self):
        self._preg(QuickFix._checkstyle_extract)

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
    def _maven_extract(line, callback):
        match = MVN_ERROR_REGEX.match(line)
        if match:
            callback(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))

    @staticmethod
    def _checkstyle_extract(line, callback):
        match = CHECKSTYLE_ERROR_REGEX.match(line)
        if match:
            callback(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))

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

