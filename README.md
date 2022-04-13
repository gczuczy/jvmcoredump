# Description

Provides reliable core dumps of JVMs during FullGC loops. This is achieved by attaching a debugger to the java process, and inserting breakpoints on the suspected entry points of libjvm's GC functionality. Once a breakpoint is hit, each threads' frames are examined not to contain any running calls that might indicate GC functionality. Once this is ensured, the core is written to a file.

Currently a similar tool has been used on Coretto, on which this rewrite is based. The development testing is using the tiny included code that forces the JVM into a GC loop, which is run with OpenJDK17 at this time.

# Installation

Get it from pip:
```
pip install jvmcoredump-gczuczy
```

Also please make sure either your libjvm.so is not stripped, or of it's stripped, you have installed the supplemental symbol tables (for ubuntu it's in the -dbg package).

# Example

Let's assume, we have a java process in a (Full)GC loop:

```
(...)
[3.068s][info   ][gc,heap     ] GC(43) Humongous regions: 0->0
[3.068s][info   ][gc,metaspace] GC(43) Metaspace: 183K(384K)->183K(384K) NonClass: 168K(256K)->168K(256K) Class: 14K(128K)
->14K(128K)
[3.068s][info   ][gc          ] GC(43) Pause Young (Normal) (G1 Preventive Collection) 1016M->1016M(1024M) 5.918ms
[3.068s][info   ][gc,cpu      ] GC(43) User=0.02s Sys=0.00s Real=0.01s
[3.068s][info   ][gc,start    ] GC(44) Pause Young (Normal) (G1 Preventive Collection)
[3.068s][info   ][gc,task     ] GC(44) Using 4 workers of 4 for evacuation
[3.075s][info   ][gc          ] GC(44) To-space exhausted
[3.075s][info   ][gc,phases   ] GC(44)   Pre Evacuate Collection Set: 0.2ms
[3.075s][info   ][gc,phases   ] GC(44)   Merge Heap Roots: 0.1ms
[3.075s][info   ][gc,phases   ] GC(44)   Evacuate Collection Set: 5.6ms
[3.075s][info   ][gc,phases   ] GC(44)   Post Evacuate Collection Set: 0.7ms
[3.075s][info   ][gc,phases   ] GC(44)   Other: 0.1ms
[3.075s][info   ][gc,heap     ] GC(44) Eden regions: 1->0(47)
[3.075s][info   ][gc,heap     ] GC(44) Survivor regions: 5->4(4)
[3.075s][info   ][gc,heap     ] GC(44) Old regions: 1012->1014
[3.075s][info   ][gc,heap     ] GC(44) Archive regions: 2->2
[3.075s][info   ][gc,heap     ] GC(44) Humongous regions: 0->0
[3.075s][info   ][gc,metaspace] GC(44) Metaspace: 183K(384K)->183K(384K) NonClass: 168K(256K)->168K(256K) Class: 14K(128K)
->14K(128K)
[3.075s][info   ][gc          ] GC(44) Pause Young (Normal) (G1 Preventive Collection) 1017M->1018M(1024M) 6.804ms
[3.075s][info   ][gc,cpu      ] GC(44) User=0.02s Sys=0.00s Real=0.01s
[3.075s][info   ][gc,start    ] GC(45) Pause Young (Normal) (G1 Preventive Collection)
[3.075s][info   ][gc,task     ] GC(45) Using 4 workers of 4 for evacuation
[3.086s][info   ][gc          ] GC(45) To-space exhausted
[3.086s][info   ][gc,phases   ] GC(45)   Pre Evacuate Collection Set: 0.2ms
[3.086s][info   ][gc,phases   ] GC(45)   Merge Heap Roots: 0.1ms
[3.086s][info   ][gc,phases   ] GC(45)   Evacuate Collection Set: 8.8ms
[3.086s][info   ][gc,phases   ] GC(45)   Post Evacuate Collection Set: 1.8ms
[3.086s][info   ][gc,phases   ] GC(45)   Other: 0.2ms
[3.087s][info   ][gc,heap     ] GC(45) Eden regions: 1->0(49)
[3.087s][info   ][gc,heap     ] GC(45) Survivor regions: 4->2(3)
[3.087s][info   ][gc,heap     ] GC(45) Old regions: 1014->1018
[3.087s][info   ][gc,heap     ] GC(45) Archive regions: 2->2
[3.087s][info   ][gc,heap     ] GC(45) Humongous regions: 0->0
[3.087s][info   ][gc,metaspace] GC(45) Metaspace: 183K(384K)->183K(384K) NonClass: 168K(256K)->168K(256K) Class: 14K(128K)
->14K(128K)
[3.087s][info   ][gc          ] GC(45) Pause Young (Normal) (G1 Preventive Collection) 1019M->1020M(1024M) 11.169ms
[3.087s][info   ][gc,cpu      ] GC(45) User=0.03s Sys=0.00s Real=0.01s
[3.087s][info   ][gc,start    ] GC(46) Pause Young (Normal) (G1 Preventive Collection)
[3.087s][info   ][gc,task     ] GC(46) Using 4 workers of 4 for evacuation
(...)
```

Launch jvmcoredump on it to get a valid core dumped:

```
$ jvmcoredump -c /tmp/foo -p $(ps auxww | awk '/java -/ && !/awk/ {print $2}')
Starting the debugger on /usr/bin/java ...
Attaching to the java process 14473 ...
Inserting breakpoints...
Inserted 2 breakpoints
Break at GangWorker::run_task, checking for GC activity
Dumping core to /tmp/foo
Enjoy
```

And now it can be used for any purposes, example:

```
$ jhsdb jmap --exe /usr/bin/java --core /tmp/foo --binaryheap --dumpfile /tmp/jmap
Attaching to core /tmp/foo from executable /usr/bin/java, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 17.0.2+8-Ubuntu-120.04
heap written to /tmp/jmap
```

# TODO

I still have to upload this to pip, so that's kind of the first item here.

When I have the time, I would like to make this work with LLDB as well - currently only gdb is implemented. I haven't yet done the complete legword to look for a machine interface for LLDB, but I guess they also have one. So, this feature is still upcoming

# Bugreports

This tool is empyrically written, meaning, it can only handle those situation which I/we have encountered. This means, there's some chance that someone will run into a jvm, which is either an untested implementation, or it's using a GC strategy that's not covered at this very moment.

Adding support for these is remarkably easy, just the symbols have to be extended.

So, if you happen to come across such a situation, please:

 - If you would like to, you can look for the missed symbols, add it to them to the symbol_ lists at cli.py, and submit a pull request
 - If you don't know how to, please submit a bug report, including the backtraces of all threads, and I will get it from there.

This is how to extract the backtraces:
Attach GDB to the java process:
```
#$ gdb `which java` $(ps auxww | awk '/java -/ && !/awk/ {print $2}')
GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
(...)
Attaching to program: /usr/bin/java, process 14539
[New LWP 14540]
[New LWP 14541]
(...)
(gdb)
```

Check the list of threads:
```
(gdb) info thr
 Id   Target Id                                           Frame
 1    Thread 0x7f251991e100 (LWP 14539) "java"            __pthread_clockjoin_ex (threadid=139797295445760,
     thread_return=thread_return@entry=0x7fff23a49e38, clockid=clockid@entry=0, abstime=abstime@entry=0x0,
         block=block@entry=true) at pthread_join_common.c:145

2    Thread 0x7f251822b700 (LWP 14540) "java"            syscall () at ../sysdeps/unix/sysv/linux/x86_64/syscall.S:38
3    Thread 0x7f24fa587700 (LWP 14541) "GC Thread#0"     0x00007f2518c9ad8a in CompressedOops::decode_raw (
     v=(unknown: -1052089560)) at ./src/hotspot/share/oops/compressedOops.hpp:94
(...)      
```

Go through them (GC* threads supposed to be enough), and get the backtrace on each:
```
(gdb) thread 3
[Switching to thread 3 (Thread 0x7f24fa587700 (LWP 14541))]
#0  0x00007f2518c9ad8a in CompressedOops::decode_raw (v=(unknown: -1052089560))
    at ./src/hotspot/share/oops/compressedOops.hpp:94
94      ./src/hotspot/share/oops/compressedOops.hpp: No such file or directory.
(gdb) bt
#0  0x00007f2518c9ad8a in CompressedOops::decode_raw (v=(unknown: -1052089560))
    at ./src/hotspot/share/oops/compressedOops.hpp:94
#1  CompressedOops::decode_not_null (v=(unknown: -1052089560)) at ./src/hotspot/share/oops/compressedOops.inline.hpp:56
#2  G1FullGCMarker::mark_and_push<narrowOop> (p=0xff01164c, this=0x7f24e0170980)
        at ./src/hotspot/share/gc/g1/g1FullGCMarker.inline.hpp:81
(..)	
```

This per-thread backtrace is needed to find the required symbols.

# History and notes

A couple of years ago $work our java devs had a really hard time finding the culprit of the repeated FullGC loops that our JVMs are falling into. While having a little chinwag on this with one of the architects, I got a thought that this may not at all be impossible to crack, because it's the java VM who's in a GC, it's not the VM which is inoperatable, but the java stack running inside it. This mean that libjvm is still doing its task, just unable to complete it.

My initial thought was that maybe a timing attack would work, because it's a loop of GC events, so at some point the jvm must leave the GC code to re-enter it immediately. So there's at least a couple of micro or nanoseconds where GC is not active, and the core is valid.

Upon attaching a gdb I've realized that I was mostly right. Where I was wrong, was I didn't need a timing technique here, just to find the calls' symbols which are initiating the GC code. Once empyrically getting these, testing showed that the coredumps acquired on the breakpoints on these symbols are indeed not corrupted.

So, after this our FullGC issues were gone in a record amount of time.

Happy customers, happy devs, and my work was appreciated with a devaluation, explained with "motivation".
