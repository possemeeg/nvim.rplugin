#!/usr/bin/python3

import neovim
import re
import importlib
import os
from os import path
import sys
import subprocess

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
import util
from util import NvimPlugin

GET_TEMPLATE = """
{indent}public {prop_type} get{prop_name_up}() {{
{indent}{indent}return {prop_name};
{indent}}}
"""
SET_TEMPLATE = """
{indent}public void set{prop_name_up}({prop_type} {prop_name}) {{
{indent}{indent}this.{prop_name} = {prop_name};
{indent}}}
"""
GET_SET_TEMPLATE = GET_TEMPLATE + SET_TEMPLATE;
PATH_MATCHER = re.compile(r'src/(test|main)/java/(.*\.java)$')
PROP_MATCHER = re.compile(r'([^\s]+\s[^\s]+);$')

@neovim.plugin
class JavaPlugin(NvimPlugin):

    def __init__(self, nvim):
        super(JavaPlugin,self).__init__(nvim)
        self.indent = self.nvim.options['shiftwidth'] * ' '

    @neovim.command('Jclass')
    def jclass(self):
        path_match = PATH_MATCHER.search(self.nvim.current.buffer.name)
        if not path_match:
            self.echo('No class and package match for path: {}'.format(self.nvim.current.buffer.name))
            return
        relative_path = path_match.group(2)
        sep = relative_path.rfind('/')
        package_name = relative_path[:sep].replace('/','.')
        class_name = relative_path[sep+1:-5]
        
        self.nvim.current.buffer.append([
            'package {};'.format(package_name),
            '',
            'public class {}'.format(class_name) + ' {',
            '',
            '}'], 0)

    @neovim.command('Jget')
    def jget(self):
        self._prop_template(GET_TEMPLATE)

    @neovim.command('Jset')
    def jset(self):
        self._prop_template(SET_TEMPLATE)

    @neovim.command('Jgetset')
    def jgetset(self):
        self._prop_template(GET_SET_TEMPLATE)

    @neovim.autocmd('BufEnter', pattern='*.java', eval='expand("<afile>")', sync=False)
    def on_bufenter(self, filename):
        bs = util.RootSeeker(path.realpath(filename), 'pom.xml').backseek(True)
        bs = bs if bs else util.RootSeeker(filename, 'main/java').backseek(True)
        if bs:
            self.nvim.options['path'] = ','.join(util.LeafDirectoryFinder(bs, re.compile(r'.*java$')).alldirs())

    def _prop_template(self, template):
        prop_match = PROP_MATCHER.search(self.nvim.current.line)
        if not prop_match:
            self.echo('No property match on current line: "{}"'.format(self.nvim.current.line.strip()))
            return
        type_prop = prop_match.group(1).strip().split(' ');
        prop_type = type_prop[0]
        prop_name = type_prop[1]

        self.nvim.funcs.setreg('"',template.format(indent=self.indent, prop_type=prop_type, prop_name=prop_name,
                    prop_name_up=prop_name[0:1].upper() + prop_name[1:]))





