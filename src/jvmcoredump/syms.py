'''
Extract the symbols from all threads in a core file.
'''

import argparse
import pathlib
import asyncio
import yaml

from . import gdb
from . import debugger

from pprint import pprint

def main():
    parser = argparse.ArgumentParser('jvmcoresyms',
                                     description="Extract the symbols from a coredump for analysis, output is YAML",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # config file support is planned, but not yet implemented
    #parser.add_argument('-C', '--config', dest='cfgfile', default=pathlib.Path(pathlib.Path.home(), '.jvmcoredump'),
    #                    help='Path to the configuration file, skipped if not found')
    parser.add_argument('-g', '--gdb', dest='gdb', default='/usr/bin/gdb',
                        help='Path to gdb')
    parser.add_argument('-j', '--java', dest='java', default='/usr/bin/java',
                        help='Path to the java executable')
    parser.add_argument('-c', '--core', dest='core', required=True,
                        help='Path of the core file to analyze')

    args = parser.parse_args()
    #pprint(args)
    
    dbg = gdb.GDB(gdbbin = args.gdb)
    asyncio.run(analyze(dbg, args.java, args.core))
    pass

async def analyze(dbg, java, core):

    print('# Opening core file {j} {c}'.format(j = java, c= core))
    await dbg.start(java, core)

    print('# Analyzing core...')
    out = {}
    # check the thread list
    threadids = await dbg.getThreadList()
    for thid in threadids:
        stack = await dbg.getThreadStack(thid);
        out['Thread #{th}'.format(th = thid)] = [frame['frame']['func'] for frame in stack]
        pass

    print(yaml.dump(out, indent=2, explicit_start=True))
    
    pass
