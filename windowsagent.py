from .agentbase import AgentBase
from .cli import CLI

class WindowsAgent(AgentBase, CLI):

    def __init__(self):

        super().__init__()
