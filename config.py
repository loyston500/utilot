import os

# Set your env first
# using `export BOT_TOKEN="token"`
token = os.environ['BOT_TOKEN']

# Set your prefix
prefix = "2b$"

# Include necessary cmds
cmds = ['cmds.utils', 'cmds.doc_cmds', 'cmds.tio', 'cmds.fundamentals', 'cmds.rand', 'cmds.server_cmds', 'cmds.db', 'cmds.pil', 'cmds.owner']

# Setting this to False will essentially disable print
debug = False

# Please, this needs to be True, for now at least!
speedups = True

# Remove mine and put your ID
ownerids = {558715694049525803}
