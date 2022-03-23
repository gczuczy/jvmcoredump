fullgc:
	javac FullGC.java

run: FullGC.class
	java -Xmx1G -Xms512M -verbose:GC -XX:+PrintGCDetails FullGC
#-XX:+PrintGCTimeStamps 

FullGC.class: fullgc
