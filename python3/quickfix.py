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
PYTHON_STACK = re.compile(r'^\s*File\s"(?P<file>[^"]+)",\sline\s(?P<line>[0-9]+)(,\s){0,1}(?P<msg>.*)$')
PYTHON_PDB_STACK = re.compile(r'^>{0,1}\s+(?P<file>[^\(]+)\((?P<line>[0-9]+)\)(?P<msg>.*)$')
PYLINT = re.compile(r'^[^:]+:(?P<line>[0-9]+):(?P<col>[0-9]+)[:\s]*(?P<msg>.*)$')
ALL = [MVN_ERROR_REGEX, CHECKSTYLE_ERROR_REGEX_8, CHECKSTYLE_ERROR_REGEX_7, PYTHON_STACK, PYTHON_PDB_STACK, PYLINT]

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
                callback(matchdict.get('type', ''), \
                        matchdict.get('file', ''), \
                        matchdict.get('line', ''), \
                        matchdict.get('col', ''), \
                        matchdict.get('msg', ''))
                return
    
if __name__ == '__main__':
    mvnline = "[ERROR] /home/peter/pmg/dev/javasimple/src/main/java/com/possemeeg/javatest/App.java:[25,15] ';' expected"

    QuickFix(None)._all_extract(mvnline, lambda sec, file, line, col, msg:
            print("mvn: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))

    cksline1 = "[ERROR] /home/peter/pmg/dev/javasimple/src/main/java/com/possemeeg/javatest/App.java:25: ';' expected"
    QuickFix(None)._all_extract(cksline1, lambda sec, file, line, col, msg:
            print("cks1: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))

    cksline2 = "[ERROR] /home/peter/pmg/dev/javasimple/src/main/java/com/possemeeg/javatest/App.java:25:15: ';' expected"
    QuickFix(None)._all_extract(cksline2, lambda sec, file, line, col, msg:
            print("cks2: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))

    cksline3 = '  File "/home/peter/Development/pmg/clubresults/src/python/ve3.7/lib/python3.7/site-packages/flask/app.py", line 2309, in __call__'
    QuickFix(None)._all_extract(cksline3, lambda sec, file, line, col, msg:
            print("cks3: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))
  
    cksline4 = '> /home/peter/Development/pmg/clubresults/src/python/ve3.7/lib/python3.7/site-packages/flask_oidc/__init__.py(657)_oidc_callback() '
    QuickFix(None)._all_extract(cksline4, lambda sec, file, line, col, msg:
            print("cks4: sev: {}, file: {}, line: {}, col: {}, msg: {}".format(sec, file, line, col, msg)))
  
    #return self.wsgi_app(environ, start_response)
