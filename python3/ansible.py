#!/usr/bin/python3

import neovim
import os
from os import path
import sys

sys.path.append(path.dirname(path.realpath(path.join(os.getcwd(), path.expanduser(__file__)))))
import util
from util import NvimPlugin

@neovim.plugin
class Ansible(NvimPlugin):

    def __init__(self, nvim):
        super(Ansible,self).__init__(nvim)

    @neovim.command('Ansdec')
    def decrype(self):
        self.nvim.command('!ansible-vault decrypt < %')
