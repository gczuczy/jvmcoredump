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
symbols_breakpoints = [
    # Coretto
    'SafepointSynchronize::begin',
    #OpenJDK17
    'GangWorker::run_task'
]
# if any of these symbols are present in any of the threads'
# backtraces, GC activity is present
symbols_gcsyms = [
    # Coretto
    'StealMarkingTask::do_it',
    'StealTask::do_it',
    'DrainStacksCompactionTask::do_it',
    'VM_ParallelGCFailedAllocation::doit',
    'StealRegionCompactionTask::do_it',
    # OpenJDK17
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

async def insert_breakpoints(dbg:debugger.Debugger):
    breakpoints = 0;
    for bp in symbols_breakpoints:
        bpres = await dbg.insertBreak(bp)
        breakpoints += 1 if bpres else 0
        pass
    return breakpoints

async def check_ingc(dbg):
    threadids = await dbg.getThreadList()
    for thid in threadids:
        stack = await dbg.getThreadStack(thid);
        for frame in stack:
            #pprint(['Checking sym', frame['frame']['func']])
            if frame['frame']['func'] in symbols_gcsyms:
                return True,frame['frame']['func']
            pass
        pass
    return False,None

async def run(dbg:debugger.Debugger, pid:int, java:str, core:str):
    #pprint(["run asd", dbg, pid, java, core]);

    # let's start the debugger
    print('Starting the debugger on {java} ... '.format(java=java))
    await dbg.start(java)

    # first we attach to the java process
    print('Attaching to the java process {pid} ...'.format(pid=pid))
    await dbg.attach(pid)

    loop = True
    print('Checkin current GC status...')
    ingc,sym = await check_ingc(dbg)
    if not ingc:
        print('Not in GC right now, skipping loop')
        loop = False

    while loop:
        # insert the breakpoints
        print('(Re)inserting breakpoints... ')
        breakpoints = await insert_breakpoints(dbg)
        if breakpoints == 0:
            print('Failed to insert breakpoints')
            return
        print('Inserted {bp} breakpoints'.format(bp=breakpoints))

        # continue now
        await dbg.continueProcess()

        # await break
        brk = await dbg.waitForBreak()

        # check whether we are in GC at the break
        print('Break at {sym}, checking for GC activity'.format(sym=brk['frame']['func']))
        ingc,sym = await check_ingc(dbg)
        if not ingc: break
        print('Still in gc symbol {sym} is on stack'.format(sym = sym))
        pass

    print('Dumping core to {f}'.format(f=core))
    await dbg.dumpCore(core)

    print('Enjoy')
    # and the bailout
    await dbg.shutdown()
    pass
