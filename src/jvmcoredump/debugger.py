'''
This module covers the abstract Debugger interface.
Will come in handy once LLVM's lldb is implemented.
'''

import abc

class Debugger(metaclass = abc.ABCMeta):

    @abc.abstractmethod
    async def start(self, java:str):
        pass

    @abc.abstractmethod
    async def shutdown(self):
        pass
    
    @abc.abstractmethod
    async def attach(self, pid: int):
        pass
    pass
