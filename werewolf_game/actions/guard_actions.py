from camelgym.actions import Action
from .common_actions import NighttimeWhispers

class Protect(NighttimeWhispers):

    def __init__(self, name="Protect", context=None, llm=None):
        super().__init__(name = name, context=context, llm = llm)
    pass
