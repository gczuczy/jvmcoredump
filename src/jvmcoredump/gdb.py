'''
This file provides the GDB interface
'''
from gdb_ctrl import GDBCtrl

from pprint import pprint

from . import debugger

class GDB(debugger.Debugger):
    def __init__(self, gdbbin:str):
        self._gdbbin = gdbbin
        self._gdb = GDBCtrl()
        self._pid = None
        pass

    def __repr__(self):
        if self._pid is not None:
            return "<GDB({g}) attached to {p}>".format(g = self._gdb,
                                           p = self._pid)
            
        return "<GDB({g})>".format(g = self._gdbbin)

    async def start(self, java:str, core:str=None):
        if core is None:
            await self._gdb.spawn(path2bin = self._gdbbin,
                                  args = [java])
        else:
            await self._gdb.spawn(path2bin = self._gdbbin,
                                  args = [java, core])
        pass

    async def shutdown(self):
        await self._gdb.shutdown();
        pass

    async def _awaitToken(self, token):
        token = int(token)
        #pprint(['Waiting for token', token]);
        while True:
            resp = await self._gdb.recv()
            data = None
            if hasattr(resp, 'as_native'):
                data = resp.as_native()
                if 'token' in data and data['token'] == token:
                    return data
                pass
            #pprint(['raw resp', resp, data])

            if resp.is_result():
                if 'class' in data and data['class'] == 'error':
                    pprint(data)
                    raise Exception('GDB attach error: {e}'.format(e=data['msg']))
            elif resp.is_async():
                if data['token'] is None or data['token'] != token and data['type'] == 'Notify':
                    continue
                raise Exception('ASync not yet implemented');
            elif resp.is_stream():
                if data['type'] in ['Console', 'Log'] :
                    continue
                raise Exception('Stream not yet implemented');
                pass
            else:
                # supposed to be a terminationrecord
                #break
                continue
                pass
            pass
        pass

    async def attach(self, pid:int):
        self._pid = pid
        token = await self._gdb.send('-target-attach {pid}'.format(pid=pid))
        resp = await self._awaitToken(token)
        pass

    async def insertBreak(self, symbol:str):
        #pprint(['Inserting breakpoint', symbol])
        token = await self._gdb.send('-break-insert {bp}'.format(bp=symbol));
        resp = await self._awaitToken(token)
        if resp is None: return False
        #pprint(resp)

        return True

    async def continueProcess(self):
        token = await self._gdb.send('-exec-continue')
        resp = await self._awaitToken(token)
        #pprint(resp)
        pass

    async def waitForBreak(self):
        '''
        wait for breaking
        '''
        while True:
            resp = await self._gdb.recv()
            data = None
            if hasattr(resp, 'as_native'):
                data = resp.as_native()
                if 'class' in data and data['class'] == 'stopped' and data['reason'] == 'breakpoint-hit':
                    return data
                pass
            pass
        pass

    async def getThreadList(self):
        '''
        This is ought to return the thread IDs
        '''
        token = await self._gdb.send('-thread-list-ids')
        resp = await self._awaitToken(token)
        #pprint(resp)
        return resp['thread-ids']['thread-id']

    async def getThreadStack(self, threadid):
        # select the thread
        token = await self._gdb.send('-thread-select {thid}'.format(thid = threadid));
        await self._awaitToken(token)

        # get the backtrace
        token = await self._gdb.send('-stack-list-frames')
        resp = await self._awaitToken(token)
        return resp['stack']

    async def dumpCore(self, corefile:str):
        token = await self._gdb.send('-interpreter-exec console "generate-core-file {f}"'
                                     .format(f=corefile));
        await self._awaitToken(token)
        pass
    pass
