'''
This module covers the abstract Debugger interface.
Will come in handy once LLVM's lldb is implemented.
'''

import abc

class Debugger(metaclass = abc.ABCMeta):

    @abc.abstractmethod
    async def start(self, java:str, core:str=None):
        pass

    @abc.abstractmethod
    async def shutdown(self):
        pass
    
    @abc.abstractmethod
    async def attach(self, pid: int):
        pass

    @abc.abstractmethod
    async def insertBreak(self, symbol:str):
        pass

    @abc.abstractmethod
    async def continueProcess(self):
        pass

    @abc.abstractmethod
    async def waitForBreak(self):
        pass

    @abc.abstractmethod
    async def getThreadList(self):
        pass

    @abc.abstractmethod
    async def getThreadStack(self, threadid):
        pass

    @abc.abstractmethod
    async def dumpCore(self, corefile:str):
        pass
    pass
