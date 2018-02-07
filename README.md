# Neovim Remote Plugins
## Installation
1. Copy contents into rplugin directory next to init.vim

Example directory structure:
```
.config/nvim/init.vim
.config/nvim/rplugin
.config/nvim/rplugin/python3
.config/nvim/rplugin/python3/java.py
```

2. Update remote plugins
```
:UpdateRemotePlugins
```

3. Restart nvim

## Example
.config/nvim/rplugin/python3/example.py
```
import neovim

@neovim.plugin
class TestPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.function("TestFunction", sync=True)
    def testfunction(self, args):
        return 3

    @neovim.command("TestCommand", range='', nargs='*')
    def testcommand(self, args, range):
        # args is array of arguments
        # range is range of selected lines
        self.nvim.current.line = ('Command with args: {}, range: {}'.format(args, range))

    @neovim.autocmd('BufEnter', pattern='*.py', eval='expand("<afile>")', sync=True)
    def on_bufenter(self, filename):
        self.nvim.out_write("testplugin is in " + filename + "\n")

```
