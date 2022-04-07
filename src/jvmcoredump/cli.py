'''
This submodule covers the command line interface
'''

import argparse
import pathlib
import asyncio

from . import gdb
from . import debugger

from pprint import pprint

# GC should be starting somewhere here
symbols_break = ['SafepointSynchronize::begin',
                 #OpenJDK17
                 'GangWorker::run_task'
]
# if any of these symbols are present in any of the threads'
# backtraces, GC activity is present
symbols_gc = [
    'StealMarkingTask::do_it',
    'StealTask::do_it',
    'DrainStacksCompactionTask::do_it',
    'VM_ParallelGCFailedAllocation::doit',
    'StealRegionCompactionTask::do_it',
    # openjdk
    'G1EvacuateRegionsBaseTask::work',
]


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
    print('Starting the debugger on {java} ... '.format(java=java))
    await dbg.start(java)

    # first we attach to the java process
    print('Attaching to the java process {pid} ...'.format(pid=pid))
    await dbg.attach(pid)

    # insert the breakpoints
    print('Inserting breakpoints... ')
    breakpoints = 0;
    for bp in symbols_break:
        bpres = await dbg.insertBreak(bp)
        breakpoints += 1 if bpres else 0
        pass
    if breakpoints == 0:
        print('Failed to insert breakpoints')
        return
    print('Inserted {bp} breakpoints'.format(bp=breakpoints))

    # and the bailout
    await dbg.shutdown()
    pass
