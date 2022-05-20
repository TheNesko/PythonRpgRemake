from pygame import time
from Engine import Game
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.screen import Screen
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.console import Group
from rich import print

Game.disable_quickedit()
Game.window('Game',50,40)

layout = Layout()
console = Console()

layout.split_column(
    Layout(name='Main',ratio=1),
    Layout(name='Side',ratio=2)
)

