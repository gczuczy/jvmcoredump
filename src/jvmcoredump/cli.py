'''
This submodule covers the command line interface
'''

import argparse
import pathlib
import asyncio

from . import gdb
from . import debugger

from pprint import pprint

def main():
    parser = argparse.ArgumentParser('jvmcoredump',
                                     description="Dump JVM cores reliably even during GC loops",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # config file support is planned, but not yet implemented
    #parser.add_argument('-C', '--config', dest='cfgfile', default=pathlib.Path(pathlib.Path.home(), '.jvmcoredump'),
    #                    help='Path to the configuration file, skipped if not found')
    parser.add_argument('-g', '--gdb', dest='gdb', default='/usr/bin/gdb',
                        help='Path to gdb')
    parser.add_argument('-j', '--java', dest='java', default='/usr/bin/java',
                        help='Path to the java executable')
    parser.add_argument('-p', '--pid', dest='pid', required=True,
                        help='PID of the running java process to attach to')
    parser.add_argument('-c', '--core', dest='core', required=True,
                        help='File to dump the core to')

    args = parser.parse_args()
    #pprint(args)
    
    dbg = gdb.GDB(gdbbin = args.gdb)
    asyncio.run(run(dbg, int(args.pid), args.java, args.core))
    pass

async def run(dbg:debugger.Debugger, pid:int, java:str, core:str):
    pprint(["run asd", dbg, pid, java, core]);

    # let's start the debugger
    await dbg.start(java)

    # first we attach to the java process
    await dbg.attach(pid)
    await dbg.shutdown()
    pass
